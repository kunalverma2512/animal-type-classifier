from ultralytics import YOLO
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Load your model with full path
model_path = SCRIPT_DIR / "cattle_model.pth"
print(f"Loading model from: {model_path}")
model = YOLO(str(model_path))

# Export to TorchScript (.pt)
print("Exporting to TorchScript format...")
model.export(format="torchscript")
print("✓ Export complete!")
