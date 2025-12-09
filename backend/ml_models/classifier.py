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
        
        # Override class names with custom cattle view classes
        # Your model has 5 classes for cattle view classification
        self.custom_class_names = {
            0: "back_view",
            1: "side_view", 
            2: "top_view",
            3: "udder",
            4: "keypoints"
        }
        
        print(f"Overriding model classes with: {list(self.custom_class_names.values())}")
        print("Cattle model loaded successfully (Ultralytics YOLO).")

    def predict(self, source):
        """
        Predict on images - processes each image individually and prints results
        
        Args:
            source: Single image path or list of image paths
        
        Returns:
            Dictionary with individual results for each image
        """
        # Handle single image or list of images
        if isinstance(source, str):
            image_paths = [source]
        else:
            image_paths = list(source)
        
        # Store results
        results_dict = {}
        
        print("\n" + "="*70)
        print(f"PROCESSING {len(image_paths)} IMAGES INDIVIDUALLY")
        print("="*70)
        
        # Process each image separately
        for idx, image_path in enumerate(image_paths, start=1):
            try:
                print(f"\nImage {idx}/{len(image_paths)}: {image_path}")
                
                # Run model on single image
                result = self.model.predict(image_path, verbose=False)
                
                # Extract classification from result
                if result and len(result) > 0:
                    res = result[0]
                    
                    # Get predicted class using custom class names
                    if hasattr(res, 'probs'):
                        top_class_idx = int(res.probs.top1)
                        
                        # Use custom class name instead of model's default
                        class_name = self.custom_class_names.get(top_class_idx, f"unknown_class_{top_class_idx}")
                        
                        confidence = float(res.probs.top1conf.item())
                        
                        # Print result
                        print(f"  ✓ Result: {class_name}")
                        print(f"  ✓ Confidence: {confidence:.4f}")
                        
                        # Store actual model output
                        results_dict[f"image_{idx}"] = str(class_name)
                    else:
                        print(f"  ⚠ No classification available")
                        results_dict[f"image_{idx}"] = "unknown"
                else:
                    print(f"  ⚠ No result from model")
                    results_dict[f"image_{idx}"] = "no_result"
                    
            except Exception as e:
                # Don't crash - log error and continue
                print(f"  ✗ Error: {str(e)}")
                results_dict[f"image_{idx}"] = f"error"
        
        print("\n" + "="*70)
        print("RESULTS SUMMARY:")
        print("="*70)
        for key, value in results_dict.items():
            print(f"  {key}: {value}")
        print("="*70 + "\n")
        
        return results_dict

def get_classifier():
    """Get classifier instance"""
    return CattleClassifier()
