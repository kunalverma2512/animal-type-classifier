# classifier.py — final stable version (always uses Ultralytics YOLO loader)
from pathlib import Path
from ultralytics import YOLO

MODEL_DIR = Path(__file__).parent
MODEL_PATH = MODEL_DIR.parent / "cattle_model_ts.pt"

class CattleClassifier:
    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

        print(f"Loading YOLO model: {MODEL_PATH}")
        self.model = YOLO(str(MODEL_PATH), task="classify")
        self.is_torchscript = False   # using YOLO loader
        print("Cattle model loaded successfully (Ultralytics YOLO).")

    def predict(self, source):
        """Predict on an image path or numpy array."""
        return self.model.predict(source)  # YOLO handles preprocessing internally
