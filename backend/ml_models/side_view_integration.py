"""
Side View Model Integration
Processes side view images for body measurements and leg analysis
"""
import json
import os
import math
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ML_MODELS_DIR = Path(__file__).parent
SIDE_VIEW_MODEL = ML_MODELS_DIR / "side_view_model_v2.pt"

SIDE_KP_NAMES = [
    "wither", "pinbone", "shoulderbone", "chest_top", "elbow",
    "body_girth_top", "rear_elbow", "spine_between_hips", "hoof",
    "belly_deepest_point", "hock", "hip_bone", "hoof_tip", "hairline_hoof"
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


def angle_with_vertical(a: Tuple[float, float], b: Tuple[float, float]) -> Optional[float]:
    """Calculate angle of line a-b with vertical axis"""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    
    if length == 0:
        return None
    
    # Angle with vertical (0 degrees = straight down)
    cos_angle = max(-1.0, min(1.0, -dy / length))
    return math.degrees(math.acos(cos_angle))


def angle_with_horizontal(a: Tuple[float, float], b: Tuple[float, float]) -> Optional[float]:
    """Calculate angle of line a-b with horizontal axis"""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    
    if length == 0:
        return None
    
    cos_angle = max(-1.0, min(1.0, dx / length))
    return math.degrees(math.acos(cos_angle))


def process_side_view(image_path: str) -> Optional[Dict]:
    """
    Process a side view image using the side view model
    
    Args:
        image_path: Path to the side view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    if not os.path.exists(image_path):
        print(f"Side view image not found: {image_path}")
        return None
    
    if not SIDE_VIEW_MODEL.exists():
        print(f"Side view model not found: {SIDE_VIEW_MODEL}")
        return None
    
    try:
        from ultralytics import YOLO
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image: {image_path}")
            return None
        
        # Load model and run inference
        model = YOLO(str(SIDE_VIEW_MODEL))
        results = model.predict(img, imgsz=640, verbose=False)
        
        if not results or len(results) == 0:
            print("No results from side view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            print("No keypoints detected in side view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()  # [num_points, 2]
        kp_map = {}
        for i, name in enumerate(SIDE_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # 1. Body Length (shoulderbone to pinbone)
        if kp_map.get("shoulderbone") and kp_map.get("pinbone"):
            length_px = dist_pixels(kp_map["shoulderbone"], kp_map["pinbone"])
            traits.append({
                "trait": "Body Length",
                "features": ["shoulderbone", "pinbone"],
                "value_px": round(length_px, 2),
                "value_cm": None,
                "score": _score_body_length(length_px)
            })
        
        # 2. Stature (wither to hoof)
        if kp_map.get("wither") and kp_map.get("hoof"):
            stature_px = dist_pixels(kp_map["wither"], kp_map["hoof"])
            traits.append({
                "trait": "Stature",
                "features": ["wither", "hoof"],
                "value_px": round(stature_px, 2),
                "value_cm": None,
                "score": _score_stature(stature_px)
            })
        
        # 3. Heart Girth (2 × chest_top to elbow)
        if kp_map.get("chest_top") and kp_map.get("elbow"):
            half_girth = dist_pixels(kp_map["chest_top"], kp_map["elbow"])
            full_girth = half_girth * 2.0
            traits.append({
                "trait": "Heart Girth",
                "features": ["chest_top", "elbow"],
                "value_px": round(full_girth, 2),
                "value_cm": None,
                "score": _score_heart_girth(full_girth)
            })
        
        # 4. Body Depth (body_girth_top to belly_deepest_point)
        if kp_map.get("body_girth_top") and kp_map.get("belly_deepest_point"):
            depth_px = dist_pixels(kp_map["body_girth_top"], kp_map["belly_deepest_point"])
            traits.append({
                "trait": "Body Depth",
                "features": ["body_girth_top", "belly_deepest_point"],
                "value_px": round(depth_px, 2),
                "value_cm": None,
                "score": _score_body_depth(depth_px)
            })
        
        # 5. Rump Angle (vertical drop between spine_between_hips and hip_bone)
        if kp_map.get("spine_between_hips") and kp_map.get("hip_bone"):
            drop_px = abs(kp_map["spine_between_hips"][1] - kp_map["hip_bone"][1])
            traits.append({
                "trait": "Rump Angle",
                "features": ["spine_between_hips", "hip_bone"],
                "value_px": round(drop_px, 2),
                "value_cm": None,
                "score": _score_rump_angle(drop_px)
            })
        
        # 6. Rear Legs Set (hock to hoof angle with horizontal)
        if kp_map.get("hock") and kp_map.get("hoof"):
            angle = angle_with_horizontal(kp_map["hock"], kp_map["hoof"])
            if angle is not None:
                traits.append({
                    "trait": "Rear Legs Set",
                    "features": ["hock", "hoof"],
                    "value_deg": round(angle, 2),
                    "value_px": None,
                    "value_cm": None,
                    "score": _score_rear_legs_set(angle)
                })
        
        # 7. Foot Angle (hairline_hoof to hoof_tip vs vertical)
        if kp_map.get("hairline_hoof") and kp_map.get("hoof_tip"):
            angle = angle_with_vertical(kp_map["hairline_hoof"], kp_map["hoof_tip"])
            if angle is not None:
                traits.append({
                    "trait": "Foot Angle",
                    "features": ["hairline_hoof", "hoof_tip"],
                    "value_deg": round(angle, 2),
                    "value_px": None,
                    "value_cm": None,
                    "score": _score_foot_angle(angle)
                })
        
        # 8. Angularity (angle at belly_deepest_point)
        if all(kp_map.get(k) for k in ["body_girth_top", "belly_deepest_point", "rear_elbow"]):
            angle = angle_at_point(
                kp_map["body_girth_top"],
                kp_map["belly_deepest_point"],
                kp_map["rear_elbow"]
            )
            if angle is not None:
                traits.append({
                    "trait": "Angularity",
                    "features": ["body_girth_top", "belly_deepest_point", "rear_elbow"],
                    "value_deg": round(angle, 2),
                    "value_px": None,
                    "value_cm": None,
                    "score": None  # Angularity typically not scored 1-9
                })
        
        print(f"✓ Side view model processed successfully")
        print(f"  Extracted {len(traits)} traits")
        
        return {
            "traits": traits,
            "meta": {
                "image_used": image_path,
                "model": "side_view_model_v2.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        print(f"Side view processing error: {e}")
        import traceback
        traceback.print_exc()
        return None


def _score_body_length(length_px: Optional[float]) -> Optional[int]:
    """Score body length (longer = higher score)"""
    if length_px is None:
        return None
    if length_px >= 350:
        return 9
    elif length_px >= 320:
        return 8
    elif length_px >= 290:
        return 7
    elif length_px >= 260:
        return 6
    elif length_px >= 230:
        return 5
    else:
        return 4


def _score_stature(height_px: Optional[float]) -> Optional[int]:
    """Score stature (taller = higher score)"""
    if height_px is None:
        return None
    if height_px >= 400:
        return 9
    elif height_px >= 370:
        return 8
    elif height_px >= 340:
        return 7
    elif height_px >= 310:
        return 6
    elif height_px >= 280:
        return 5
    else:
        return 4


def _score_heart_girth(girth_px: Optional[float]) -> Optional[int]:
    """Score heart girth (larger = higher score)"""
    if girth_px is None:
        return None
    if girth_px >= 500:
        return 9
    elif girth_px >= 460:
        return 8
    elif girth_px >= 420:
        return 7
    elif girth_px >= 380:
        return 6
    elif girth_px >= 340:
        return 5
    else:
        return 4


def _score_body_depth(depth_px: Optional[float]) -> Optional[int]:
    """Score body depth (deeper = higher score)"""
    if depth_px is None:
        return None
    if depth_px >= 180:
        return 9
    elif depth_px >= 160:
        return 8
    elif depth_px >= 140:
        return 7
    elif depth_px >= 120:
        return 6
    elif depth_px >= 100:
        return 5
    else:
        return 4


def _score_rump_angle(drop_px: Optional[float]) -> Optional[int]:
    """Score rump angle (moderate drop is ideal)"""
    if drop_px is None:
        return None
    # Moderate drop (20-40px) is ideal
    if 25 <= drop_px <= 35:
        return 9
    elif 20 <= drop_px <= 40:
        return 8
    elif 15 <= drop_px <= 45:
        return 7
    elif 10 <= drop_px <= 50:
        return 6
    else:
        return 5


def _score_rear_legs_set(angle_deg: Optional[float]) -> Optional[int]:
    """Score rear legs set angle"""
    if angle_deg is None:
        return None
    # Moderate angle (close to straight down, ~160-170°) is ideal
    if 160 <= angle_deg <= 170:
        return 9
    elif 155 <= angle_deg <= 175:
        return 8
    elif 150 <= angle_deg <= 180:
        return 7
    else:
        return 6


def _score_foot_angle(angle_deg: Optional[float]) -> Optional[int]:
    """Score foot angle (45-50° is ideal)"""
    if angle_deg is None:
        return None
    if 45 <= angle_deg <= 50:
        return 9
    elif 42 <= angle_deg <= 53:
        return 8
    elif 40 <= angle_deg <= 55:
        return 7
    elif 38 <= angle_deg <= 58:
        return 6
    else:
        return 5


def extract_side_traits(side_data: Dict) -> List[Dict]:
    """Extract and format traits from side view model output"""
    if not side_data or 'traits' not in side_data:
        return []
    
    formatted_traits = []
    
    for trait in side_data['traits']:
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
        print(f"Testing side view model with: {test_image}")
        result = process_side_view(test_image)
        if result:
            print(json.dumps(result, indent=2))
            print("\nFormatted traits:")
            traits = extract_side_traits(result)
            for t in traits:
                print(f"  - {t['trait']}: score={t['score']}, measurement={t['measurement']}")
    else:
        print("Usage: python side_view_integration.py <image_path>")
