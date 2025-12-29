# ML Models Directory

This directory contains all machine learning models and their integration modules for cattle trait analysis.

## Model Files (.pt)

YOLOv8 keypoint detection models (~40 MB each):

| Model File | Keypoints | Purpose |
|-----------|-----------|---------|
| `side_view_model_v2.pt` | 14 | Body measurements, legs, rump angle |
| `rear_view_model.pt` | 8 | Rump width, rear legs analysis |
| `top_view_model.pt` | 8 | Chest width measurement |
| `udder_view_model.pt` | 8 | Teat measurements (4 pairs) |
| `cattle_side_udder.pt`` | 5 | Udder attachment and depth |

**Total size**: ~200 MB

## Integration Modules (.py)

Python wrappers for each model:

| Integration File | Model Used | Traits Extracted |
|-----------------|------------|------------------|
| `side_view_integration.py` | side_view_model_v2.pt | 8 traits (body, legs) |
| `rear_view_integration.py` | rear_view_model.pt | 2 traits (rump, legs) |
| `top_view_integration.py` | top_view_model.pt | 1 trait (chest width) |
| `udder_view_integration.py` | udder_view_model.pt | 6 traits (teats, udder) |
| `side_udder_integration.py` | cattle_side_udder.pt | 3 traits (attachment, depth) |
| `bcs_integration.py` | N/A (placeholder) | Body condition score |

## Notebooks

- `bcs-cow-py.ipynb`: Research/development notebook for BCS analysis

## Usage

Each integration module can be used standalone:

```python
from ml_models.side_view_integration import process_side_view

# Process an image
result = process_side_view("path/to/image.jpg")
print(result['traits'])  # List of detected traits with scores
```

Or through the main AI service:

```python
from app.services.ai_service import ai_service

# Processes all 5 views automatically
results = await ai_service.classify_animal(
    image_paths=[rear, side, top, udder, side_udder],
    animal_info={...}
)
```

## File Naming Convention

- `{view}_integration.py`: Integration wrapper for a specific view
- `{view}_model.pt` or `{view}_model_v2.pt`: Trained YOLO model
- Models and integrations share the same base name for clarity

## Dependencies

All integration modules require:
- `ultralytics` (YOLOv8)
- `opencv-python`
- `numpy`
- `torch` & `torchvision`

Install via: `pip install -r requirements.txt`
