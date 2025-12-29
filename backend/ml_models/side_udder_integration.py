"""
Side-Udder View Model Integration  
Processes side-udder view (using cattle_side_udder.pt) for udder attachment and depth analysis
"""
import json
import os
import math
import logging
import gc
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .model_downloader import get_model_path

logger = logging.getLogger(__name__)

ML_MODELS_DIR = Path(__file__).parent

SIDE_UDDER_KP_NAMES = [
    "udder", "intersection", "abdomen", "hock", "udder_bottom"
]






def dist_pixels(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_at_point(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> Optional[float]:
    """Calculate angle at point b formed by points a-b-c"""
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    
    norm_ba = math.hypot(ba[0], ba[1])
    norm_bc = math.hypot(bc[0], bc[1])
    
    if norm_ba == 0 or norm_bc == 0:
        return None
    
    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    cos_angle = max(-1.0, min(1.0, dot_product / (norm_ba * norm_bc)))
    
    return math.degrees(math.acos(cos_angle))


def process_side_udder_view(image_path: str) -> Optional[Dict]:
    """
    Process a side-udder view image using the cattle_side_udder model.
    Loads model, runs inference, then explicitly unloads to free RAM.
    
    Args:
        image_path: Path to the side-udder view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    logger.info(f"Processing side-udder view: {image_path}")
    
    if not os.path.exists(image_path):
        logger.error(f"Side-udder view image not found: {image_path}")
        return None
    
    # Get model path (downloads if needed)
    model_path = get_model_path("cattle_side_udder.pt")
    if model_path is None:
        logger.error("Failed to get side-udder view model path")
        return None
    
    model = None
    try:
        # LOAD: Load model into RAM
        logger.info("Loading cattle_side_udder.pt into RAM...")
        from ultralytics import YOLO
        import time
        
        load_start = time.time()
        model = YOLO(str(model_path))
        load_time = time.time() - load_start
        logger.info(f"Side-udder model loaded in {load_time:.2f}s")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        
        # INFER: Run inference
        logger.info("Running side-udder inference...")
        infer_start = time.time()
        results = model.predict(img, imgsz=640, verbose=False)
        infer_time = time.time() - infer_start
        logger.info(f"Side-udder inference completed in {infer_time:.2f}s")
        
        if not results or len(results) == 0:
            print("No results from side-udder view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            print("No keypoints detected in side-udder view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()  # [num_points, 2]
        kp_map = {}
        for i, name in enumerate(SIDE_UDDER_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # 1. Fore Udder Attachment (angle at intersection point)
        fua_angle = None
        if all(kp_map.get(k) for k in ["udder", "intersection", "abdomen"]):
            fua_angle = angle_at_point(
                kp_map["udder"],
                kp_map["intersection"],
                kp_map["abdomen"]
            )
            if fua_angle is not None:
                traits.append({
                    "trait": "Fore Udder Attachment",
                    "features": ["udder", "intersection", "abdomen"],
                    "value_deg": round(fua_angle, 2),
                    "value_px": None,
                    "value_cm": None,
                    "score": _score_fore_udder_attachment(fua_angle)
                })
        
        # 2. Udder Depth (vertical distance from hock to udder_bottom)
        udder_depth_px = None
        if kp_map.get("hock") and kp_map.get("udder_bottom"):
            # Vertical distance
            udder_depth_px = abs(kp_map["hock"][1] - kp_map["udder_bottom"][1])
            traits.append({
                "trait": "Udder Depth",
                "features": ["hock", "udder_bottom"],
                "value_px": round(udder_depth_px, 2),
                "value_cm": None,
                "score": _score_udder_depth(udder_depth_px)
            })
        
        # 3. Central Ligament (distance from udder to intersection - depth of cleft)
        central_lig_px = None
        if kp_map.get("udder") and kp_map.get("intersection"):
            central_lig_px = dist_pixels(kp_map["udder"], kp_map["intersection"])
            traits.append({
                "trait": "Central Ligament",
                "features": ["udder", "intersection"],
                "value_px": round(central_lig_px, 2),
                "value_cm": None,
                "score": _score_central_ligament(central_lig_px)
            })
        
        print(f"✓ Side-udder view model processed successfully")
        print(f"  Extracted {len(traits)} traits")
        
        return {
            "traits": traits,
            "meta": {
                "image_used": image_path,
                "model": "cattle_side_udder.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        logger.exception(f"Error processing side-udder view: {str(e)}")
        return None
        
    finally:
        # UNLOAD: Explicitly free model from RAM
        if model is not None:
            logger.info("Unloading side_udder model from RAM...")
            del model
            gc.collect()
            logger.info("Side-udder model unloaded, memory freed")


def _score_fore_udder_attachment(angle_deg: Optional[float]) -> Optional[int]:
    """Score fore udder attachment (larger angle = tighter/better attachment)"""
    if angle_deg is None:
        return None
    
    # Larger angle indicates stronger attachment
    if angle_deg >= 140:
        return 9
    elif angle_deg >= 130:
        return 8
    elif angle_deg >= 120:
        return 7
    elif angle_deg >= 110:
        return 6
    elif angle_deg >= 100:
        return 5
    elif angle_deg >= 90:
        return 4
    else:
        return 3


def _score_udder_depth(depth_px: Optional[float]) -> Optional[int]:
    """Score udder depth (moderate depth = better, not too shallow or too deep)"""
    if depth_px is None:
        return None
    
    # Moderate depth is ideal (above hock but not too high)
    if 20 <= depth_px <= 40:
        return 9
    elif 15 <= depth_px <= 50:
        return 8
    elif 10 <= depth_px <= 60:
        return 7
    elif 5 <= depth_px <= 70:
        return 6
    else:
        return 5


def _score_central_ligament(depth_px: Optional[float]) -> Optional[int]:
    """Score central ligament (deeper cleft = better definition)"""
    if depth_px is None:
        return None
    
    # Deeper cleft indicates better ligament definition
    if depth_px >= 50:
        return 9
    elif depth_px >= 45:
        return 8
    elif depth_px >= 40:
        return 7
    elif depth_px >= 35:
        return 6
    elif depth_px >= 30:
        return 5
    else:
        return 4


def extract_side_udder_traits(side_udder_data: Dict) -> List[Dict]:
    """Extract and format traits from side-udder view model output"""
    if not side_udder_data or 'traits' not in side_udder_data:
        return []
    
    formatted_traits = []
    
    for trait in side_udder_data['traits']:
        # Get measurement value (prefer cm, fallback to px or degrees)
        measurement = trait.get('value_cm')
        if measurement is None:
            measurement = trait.get('value_deg')
        if measurement is None:
            measurement = trait.get('value_px')
        
        formatted_traits.append({
            'trait': trait.get('trait', 'Unknown'),
            'score': trait.get('score'),
            'measurement': measurement
        })
    
    return formatted_traits


if __name__ == "__main__":
    # Test the integration
    import sys
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
        print(f"Testing side-udder view model with: {test_image}")
        result = process_side_udder_view(test_image)
        if result:
            print(json.dumps(result, indent=2))
            print("\nFormatted traits:")
            traits = extract_side_udder_traits(result)
            for t in traits:
                print(f"  - {t['trait']}: score={t['score']}, measurement={t['measurement']}")
    else:
        print("Usage: python side_udder_integration.py <image_path>")
