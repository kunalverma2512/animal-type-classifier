"""
Udder View Model Integration
Processes udder view images for teat and udder analysis
"""
import json
import os
import math
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .model_downloader import get_model_path

ML_MODELS_DIR = Path(__file__).parent

UDDER_KP_NAMES = [
    "pt_1", "pt_2",  # Front left teat (base, tip)
    "pt_3", "pt_4",  # Front right teat (base, tip)
    "pt_5", "pt_6",  # Rear left teat (base, tip)
    "pt_7", "pt_8"   # Rear right teat (base, tip)
]


def dist_pixels(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def process_udder_view(image_path: str) -> Optional[Dict]:
    """
    Process an udder view image using the udder view model
    
    Args:
        image_path: Path to the udder view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    if not os.path.exists(image_path):
        print(f"Udder view image not found: {image_path}")
        return None
    
    # Get model path (downloads if needed)
    udder_view_model = get_model_path("udder_view_model.pt")
    if udder_view_model is None:
        print("Failed to load udder view model")
        return None
    
    try:
        from ultralytics import YOLO
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image: {image_path}")
            return None
        
        # Load model and run inference
        model = YOLO(str(udder_view_model))
        results = model.predict(img, imgsz=640, verbose=False)
        
        if not results or len(results) == 0:
            print("No results from udder view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            print("No keypoints detected in udder view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()  # [num_points, 2]
        kp_map = {}
        for i, name in enumerate(UDDER_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # 1. Front Teat Placement (distance between front teat bases)
        front_teat_px = None
        if kp_map.get("pt_1") and kp_map.get("pt_3"):
            front_teat_px = dist_pixels(kp_map["pt_1"], kp_map["pt_3"])
            traits.append({
                "trait": "Front Teat Placement",
                "features": ["pt_1", "pt_3"],
                "value_px": round(front_teat_px, 2),
                "value_cm": None,
                "score": _score_teat_placement(front_teat_px)
            })
        
        # 2. Rear Teat Placement (distance between rear teat bases)
        rear_teat_px = None
        if kp_map.get("pt_5") and kp_map.get("pt_7"):
            rear_teat_px = dist_pixels(kp_map["pt_5"], kp_map["pt_7"])
            traits.append({
                "trait": "Rear Teat Placement",
                "features": ["pt_5", "pt_7"],
                "value_px": round(rear_teat_px, 2),
                "value_cm": None,
                "score": _score_teat_placement(rear_teat_px)
            })
        
        # 3. Teat Length (average of 4 teats)
        teat_lengths = []
        for base, tip in [("pt_1", "pt_2"), ("pt_3", "pt_4"), ("pt_5", "pt_6"), ("pt_7", "pt_8")]:
            if kp_map.get(base) and kp_map.get(tip):
                length = dist_pixels(kp_map[base], kp_map[tip])
                teat_lengths.append(length)
        
        if teat_lengths:
            avg_length = sum(teat_lengths) / len(teat_lengths)
            traits.append({
                "trait": "Teat Length",
                "features": ["pt_1", "pt_2", "pt_3", "pt_4", "pt_5", "pt_6", "pt_7", "pt_8"],
                "value_px": round(avg_length, 2),
                "value_cm": None,
                "score": _score_teat_length(avg_length)
            })
            
            # 4. Teat Thickness (proxy: length / 3)
            teat_thickness = avg_length / 3.0
            traits.append({
                "trait": "Teat Thickness",
                "features": ["derived from teat length"],
                "value_px": round(teat_thickness, 2),
                "value_cm": None,
                "score": _score_teat_thickness(teat_thickness)
            })
        
        # 5. Rear Udder Width (distance between rear teats horizontally)
        if kp_map.get("pt_5") and kp_map.get("pt_7"):
            rear_udder_width = dist_pixels(kp_map["pt_5"], kp_map["pt_7"])
            traits.append({
                "trait": "Rear Udder Width",
                "features": ["pt_5", "pt_7"],
                "value_px": round(rear_udder_width, 2),
                "value_cm": None,
                "score": _score_rear_udder_width(rear_udder_width)
            })
        
        # 6. Rear Udder Height (approximate: vertical distance of rear teats from bottom)
        if kp_map.get("pt_5") and kp_map.get("pt_7"):
            avg_y = (kp_map["pt_5"][1] + kp_map["pt_7"][1]) / 2
            img_height = img.shape[0]
            rear_udder_height = img_height - avg_y
            traits.append({
                "trait": "Rear Udder Height",
                "features": ["pt_5", "pt_7"],
                "value_px": round(rear_udder_height, 2),
                "value_cm": None,
                "score": _score_rear_udder_height(rear_udder_height)
            })
        
        print(f"✓ Udder view model processed successfully")
        print(f"  Extracted {len(traits)} traits")
        
        return {
            "traits": traits,
            "meta": {
                "image_used": image_path,
                "model": "udder_view_model.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        print(f"Udder view processing error: {e}")
        import traceback
        traceback.print_exc()
        return None


def _score_teat_placement(distance_px: Optional[float]) -> Optional[int]:
    """Score teat placement (ideal: moderate distance)"""
    if distance_px is None:
        return None
    
    # Moderate spacing is ideal
    if 60 <= distance_px <= 80:
        return 9
    elif 55 <= distance_px <= 85:
        return 8
    elif 50 <= distance_px <= 90:
        return 7
    elif 45 <= distance_px <= 95:
        return 6
    elif 40 <= distance_px <= 100:
        return 5
    elif 35 <= distance_px <= 105:
        return 4
    elif 30 <= distance_px <= 110:
        return 3
    else:
        return 2


def _score_teat_length(length_px: Optional[float]) -> Optional[int]:
    """Score teat length (ideal: moderate length)"""
    if length_px is None:
        return None
    
    # Moderate length is ideal
    if 40 <= length_px <= 60:
        return 9
    elif 35 <= length_px <= 65:
        return 8
    elif 30 <= length_px <= 70:
        return 7
    elif 25 <= length_px <= 75:
        return 6
    elif 20 <= length_px <= 80:
        return 5
    else:
        return 3


def _score_teat_thickness(thickness_px: Optional[float]) -> Optional[int]:
    """Score teat thickness (ideal: moderate thickness)"""
    if thickness_px is None:
        return None
    
    # Moderate thickness is ideal
    if 12 <= thickness_px <= 18:
        return 9
    elif 10 <= thickness_px <= 20:
        return 8
    elif 8 <= thickness_px <= 22:
        return 7
    elif 6 <= thickness_px <= 24:
        return 6
    else:
        return 5


def _score_rear_udder_width(width_px: Optional[float]) -> Optional[int]:
    """Score rear udder width (wider = better)"""
    if width_px is None:
        return None
    
    if width_px >= 100:
        return 9
    elif width_px >= 90:
        return 8
    elif width_px >= 80:
        return 7
    elif width_px >= 70:
        return 6
    elif width_px >= 60:
        return 5
    else:
        return 4


def _score_rear_udder_height(height_px: Optional[float]) -> Optional[int]:
    """Score rear udder height (higher = better support)"""
    if height_px is None:
        return None
    
    if height_px >= 200:
        return 9
    elif height_px >= 180:
        return 8
    elif height_px >= 160:
        return 7
    elif height_px >= 140:
        return 6
    elif height_px >= 120:
        return 5
    else:
        return 4


def extract_udder_traits(udder_data: Dict) -> List[Dict]:
    """Extract and format traits from udder view model output"""
    if not udder_data or 'traits' not in udder_data:
        return []
    
    formatted_traits = []
    
    for trait in udder_data['traits']:
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
        print(f"Testing udder view model with: {test_image}")
        result = process_udder_view(test_image)
        if result:
            print(json.dumps(result, indent=2))
            print("\nFormatted traits:")
            traits = extract_udder_traits(result)
            for t in traits:
                print(f"  - {t['trait']}: score={t['score']}, measurement={t['measurement']}")
    else:
        print("Usage: python udder_view_integration.py <image_path>")
