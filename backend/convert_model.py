"""
Attempt to convert cattle_model.pth to YOLO .pt format
This tries different YOLO model architectures
"""
import torch
from ultralytics import YOLO

# Load the state dict
print("Loading cattle_model.pth...")
state_dict = torch.load('ml_models/cattle_model.pth', map_location='cpu')
print(f"✓ Loaded state_dict with {len(state_dict)} layers\n")

# Try different YOLO model sizes
yolo_models = [
    'yolo11m-cls.pt',  # YOLO11 medium classifier
    'yolo11n-cls.pt',  # YOLO11 nano classifier
    'yolo11s-cls.pt',  # YOLO11 small classifier
    'yolov8m-cls.pt',  # YOLOv8 medium classifier
    'yolov8n-cls.pt',  # YOLOv8 nano classifier
]

for model_name in yolo_models:
    try:
        print(f"\nTrying {model_name}...")
        
        # Load base model
        model = YOLO(model_name)
        
        # Get model's state dict keys
        model_keys = set(model.model.state_dict().keys())
        custom_keys = set(state_dict.keys())
        
        # Check compatibility
        matching_keys = model_keys & custom_keys
        print(f"  Matching keys: {len(matching_keys)}/{len(custom_keys)}")
        
        if len(matching_keys) > len(custom_keys) * 0.8:  # 80% match
            print(f"  ✓ Good match! Attempting conversion...")
            
            # Try to load the weights
            model.model.load_state_dict(state_dict, strict=False)
            
            # Save as proper YOLO .pt file
            output_file = 'ml_models/cattle_model_converted.pt'
            model.save(output_file)
            
            print(f"  ✅ SUCCESS! Saved to {output_file}")
            print(f"\n🎉 Conversion complete! Use 'cattle_model_converted.pt' in your code.")
            break
        else:
            print(f"  ❌ Poor match, trying next...")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        continue
else:
    print("\n❌ Could not find matching YOLO architecture.")
    print("Please ask your team member:")
    print("  1. What YOLO version was used? (e.g., yolo11m-cls)")
    print("  2. How many classes does the model have?")
    print("  3. Can they provide the .pt file instead?")
