"""
Rear View Model Integration
Processes rear view images for rump and leg analysis
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

# Configure logging
logger = logging.getLogger(__name__)

ML_MODELS_DIR = Path(__file__).parent

REAR_KP_NAMES = [
    "pin_bone_1", "pin_bone_2",
    "hip_bone_1", "hip_bone_2",
    "hock_1", "hock_2",
    "hoof_1", "hoof_2"
]



def dist_pixels(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def process_rear_view(image_path: str) -> Optional[Dict]:
    """
    Process a rear view image using the rear view model.
    Loads model, runs inference, then explicitly unloads to free RAM.
    
    Args:
        image_path: Path to the rear view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    logger.info(f"Processing rear view: {image_path}")
    
    if not os.path.exists(image_path):
        logger.error(f"Rear view image not found: {image_path}")
        return None
    
    # Get model path (downloads if needed)
    model_path = get_model_path("rear_view_model.pt")
    if model_path is None:
        logger.error("Failed to get rear view model path")
        return None
    
    model = None
    try:
        # LOAD: Load model into RAM
        logger.info("Loading rear_view_model.pt into RAM...")
        from ultralytics import YOLO
        import time
        
        load_start = time.time()
        model = YOLO(str(model_path))
        load_time = time.time() - load_start
        logger.info(f"Rear view model loaded in {load_time:.2f}s")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        
        # INFER: Run inference
        logger.info("Running rear view inference...")
        infer_start = time.time()
        results = model.predict(img, imgsz=640, verbose=False)
        infer_time = time.time() - infer_start
        logger.info(f"Rear view inference completed in {infer_time:.2f}s")
        
        if not results or len(results) == 0:
            logger.warning("No results from rear view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            logger.warning("No keypoints detected in rear view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()
        kp_map = {}
        for i, name in enumerate(REAR_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # 1. Rump Width
        if kp_map.get("pin_bone_1") and kp_map.get("pin_bone_2"):
            rump_width_px = dist_pixels(kp_map["pin_bone_1"], kp_map["pin_bone_2"])
            traits.append({
                "trait": "Rump Width",
                "features": ["pin_bone_1", "pin_bone_2"],
                "value_px": round(rump_width_px, 2),
                "value_cm": None,
                "score": _score_rump_width(rump_width_px)
            })
        
        # 2. Rear Legs Rear View
        if all(kp_map.get(k) for k in ["hock_1", "hock_2", "hoof_1", "hoof_2"]):
            hock_dist = dist_pixels(kp_map["hock_1"], kp_map["hock_2"])
            hoof_dist = dist_pixels(kp_map["hoof_1"], kp_map["hoof_2"])
            rear_legs_px = hoof_dist - hock_dist
            traits.append({
                "trait": "Rear Legs Rear View",
                "features": ["hock_1", "hock_2", "hoof_1", "hoof_2"],
                "value_px": round(rear_legs_px, 2),
                "value_cm": None,
                "score": _score_rear_legs_rear_view(rear_legs_px)
            })
        
        logger.info(f"Rear view processed: {len(traits)} traits extracted")
        
        return {
            "traits": traits,
            "keypoints": kp_map,
            "meta": {
                "image_used": image_path,
                "model": "rear_view_model.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        logger.exception(f"Error processing rear view: {str(e)}")
        return None
        
    finally:
        # UNLOAD: Explicitly free model from RAM
        if model is not None:
            logger.info("Unloading rear_view_model from RAM...")
            del model
            gc.collect()  # Force garbage collection
            logger.info("Rear view model unloaded, memory freed")


def _score_rump_width(width_px: Optional[float]) -> Optional[int]:
    """
    Score rump width on 1-9 scale
    Wider rump = higher score (more desirable)
    """
    if width_px is None:
        return None
    
    # Approximate scoring based on pixel width
    # These thresholds would ideally come from breed-specific tables
    if width_px >= 280:
        return 9
    elif width_px >= 260:
        return 8
    elif width_px >= 240:
        return 7
    elif width_px >= 220:
        return 6
    elif width_px >= 200:
        return 5
    elif width_px >= 180:
        return 4
    elif width_px >= 160:
        return 3
    elif width_px >= 140:
        return 2
    else:
        return 1


def _score_rear_legs_rear_view(delta_px: Optional[float]) -> Optional[int]:
    """
    Score rear legs rear view on 1-9 scale
    Parallel legs (delta close to 0) = higher score
    """
    if delta_px is None:
        return None
    
    abs_delta = abs(delta_px)
    
    # Scoring: smaller delta = better
    if abs_delta <= 5:
        return 9
    elif abs_delta <= 10:
        return 8
    elif abs_delta <= 15:
        return 7
    elif abs_delta <= 20:
        return 6
    elif abs_delta <= 30:
        return 5
    elif abs_delta <= 40:
        return 4
    elif abs_delta <= 50:
        return 3
    elif abs_delta <= 60:
        return 2
    else:
        return 1


def extract_rear_traits(rear_data: Dict) -> List[Dict]:
    """
    Extract and format traits from rear view model output
    
    Args:
        rear_data: Raw output from rear view model
        
    Returns:
        List of trait dictionaries
    """
    if not rear_data or 'traits' not in rear_data:
        return []
    
    formatted_traits = []
    
    for trait in rear_data['traits']:
        # Get measurement value (prefer cm, fallback to px)
        measurement = trait.get('value_cm')
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
        print(f"Testing rear view model with: {test_image}")
        result = process_rear_view(test_image)
        if result:
            print(json.dumps(result, indent=2))
            print("\nFormatted traits:")
            traits = extract_rear_traits(result)
            for t in traits:
                print(f"  - {t['trait']}: score={t['score']}, measurement={t['measurement']}")
    else:
        print("Usage: python rear_view_integration.py <image_path>")
