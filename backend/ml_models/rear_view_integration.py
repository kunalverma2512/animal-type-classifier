"""
Rear View Model Integration
Processes rear view images for rump and leg analysis
"""
import json
import os
import math
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ML_MODELS_DIR = Path(__file__).parent
REAR_VIEW_MODEL = ML_MODELS_DIR / "rear_view_model.pt"

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
    Process a rear view image using the rear view model
    
    Args:
        image_path: Path to the rear view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    if not os.path.exists(image_path):
        print(f"Rear view image not found: {image_path}")
        return None
    
    if not REAR_VIEW_MODEL.exists():
        print(f"Rear view model not found: {REAR_VIEW_MODEL}")
        return None
    
    try:
        from ultralytics import YOLO
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image: {image_path}")
            return None
        
        # Load model and run inference
        model = YOLO(str(REAR_VIEW_MODEL))
        results = model.predict(img, imgsz=640, verbose=False)
        
        if not results or len(results) == 0:
            print("No results from rear view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            print("No keypoints detected in rear view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()  # [num_points, 2]
        kp_map = {}
        for i, name in enumerate(REAR_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # 1. Rump Width (pin_bone_1 to pin_bone_2)
        rump_width_px = None
        if kp_map.get("pin_bone_1") and kp_map.get("pin_bone_2"):
            rump_width_px = dist_pixels(kp_map["pin_bone_1"], kp_map["pin_bone_2"])
            traits.append({
                "trait": "Rump Width",
                "features": ["pin_bone_1", "pin_bone_2"],
                "value_px": round(rump_width_px, 2),
                "value_cm": None,  # No scale calibration
                "score": _score_rump_width(rump_width_px)
            })
        
        # 2. Rear Legs Rear View (toe-in/toe-out)
        # Measure difference in width at hock vs hoof
        rear_legs_px = None
        if all(kp_map.get(k) for k in ["hock_1", "hock_2", "hoof_1", "hoof_2"]):
            hock_dist = dist_pixels(kp_map["hock_1"], kp_map["hock_2"])
            hoof_dist = dist_pixels(kp_map["hoof_1"], kp_map["hoof_2"])
            rear_legs_px = hoof_dist - hock_dist  # >0 = toe-out, <0 = toe-in
            traits.append({
                "trait": "Rear Legs Rear View",
                "features": ["hock_1", "hock_2", "hoof_1", "hoof_2"],
                "value_px": round(rear_legs_px, 2),
                "value_cm": None,
                "score": _score_rear_legs_rear_view(rear_legs_px)
            })
        
        print(f"✓ Rear view model processed successfully")
        print(f"  Extracted {len(traits)} traits")
        
        return {
            "traits": traits,
            "meta": {
                "image_used": image_path,
                "model": "rear_view_model.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        print(f"Rear view processing error: {e}")
        import traceback
        traceback.print_exc()
        return None


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
