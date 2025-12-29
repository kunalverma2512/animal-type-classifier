"""
Top View Model Integration  
Processes top view images for chest width analysis
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

TOP_KP_NAMES = [
    "shoulder_1", "pt_2", "pt_3", "abdomen_width_1",
    "shoulder_2", "pt_6", "spine_bw_hips", "abdomen_width_2"
]






def dist_pixels(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def process_top_view(image_path: str) -> Optional[Dict]:
    """
    Process a top view image using the top view model
    
    Args:
        image_path: Path to the top view image
        
    Returns:
        Dictionary with traits, scores, and measurements
        Returns None if processing fails
    """
    if not os.path.exists(image_path):
        print(f"Top view image not found: {image_path}")
        return None
    
    # Get model path (downloads if needed)
    top_view_model = get_model_path("top_view_model.pt")
    if top_view_model is None:
        print("Failed to load top view model")
        return None
    
    try:
        from ultralytics import YOLO
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image: {image_path}")
            return None
        
        # Load model and run inference
        model = YOLO(str(top_view_model))
        results = model.predict(img, imgsz=640, verbose=False)
        
        if not results or len(results) == 0:
            print("No results from top view model")
            return None
        
        r = results[0]
        if not hasattr(r, 'keypoints') or r.keypoints is None:
            print("No keypoints detected in top view")
            return None
        
        # Extract keypoints
        xy = r.keypoints.xy[0].cpu().numpy()  # [num_points, 2]
        kp_map = {}
        for i, name in enumerate(TOP_KP_NAMES):
            if i < xy.shape[0]:
                kp_map[name] = (float(xy[i, 0]), float(xy[i, 1]))
            else:
                kp_map[name] = None
        
        # Calculate traits
        traits = []
        
        # Chest Width (shoulder_1 to shoulder_2)
        chest_width_px = None
        if kp_map.get("shoulder_1") and kp_map.get("shoulder_2"):
            chest_width_px = dist_pixels(kp_map["shoulder_1"], kp_map["shoulder_2"])
            traits.append({
                "trait": "Chest Width",
                "features": ["shoulder_1", "shoulder_2"],
                "value_px": round(chest_width_px, 2),
                "value_cm": None,  # No scale calibration
                "score": _score_chest_width(chest_width_px)
            })
        
        print(f"✓ Top view model processed successfully")
        print(f"  Extracted {len(traits)} traits")
        
        return {
            "traits": traits,
            "meta": {
                "image_used": image_path,
                "model": "top_view_model.pt",
                "keypoints_detected": sum(1 for v in kp_map.values() if v is not None)
            }
        }
        
    except Exception as e:
        print(f"Top view processing error: {e}")
        import traceback
        traceback.print_exc()
        return None


def _score_chest_width(width_px: Optional[float]) -> Optional[int]:
    """
    Score chest width on 1-9 scale
    Wider chest = higher score (more desirable)
    """
    if width_px is None:
        return None
    
    # Approximate scoring based on pixel width
    if width_px >= 300:
        return 9
    elif width_px >= 280:
        return 8
    elif width_px >= 260:
        return 7
    elif width_px >= 240:
        return 6
    elif width_px >= 220:
        return 5
    elif width_px >= 200:
        return 4
    elif width_px >= 180:
        return 3
    elif width_px >= 160:
        return 2
    else:
        return 1


def extract_top_traits(top_data: Dict) -> List[Dict]:
    """
    Extract and format traits from top view model output
    
    Args:
        top_data: Raw output from top view model
        
    Returns:
        List of trait dictionaries
    """
    if not top_data or 'traits' not in top_data:
        return []
    
    formatted_traits = []
    
    for trait in top_data['traits']:
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
        print(f"Testing top view model with: {test_image}")
        result = process_top_view(test_image)
        if result:
            print(json.dumps(result, indent=2))
            print("\nFormatted traits:")
            traits = extract_top_traits(result)
            for t in traits:
                print(f"  - {t['trait']}: score={t['score']}, measurement={t['measurement']}")
    else:
        print("Usage: python top_view_integration.py <image_path>")
