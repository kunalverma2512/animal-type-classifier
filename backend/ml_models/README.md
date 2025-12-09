# ML Models Directory

This directory contains the machine learning model files for livestock classification.

## Files to Add:

1. **Model File (.pth)**: PyTorch model weights
   - Place your trained model `.pth` file here
   
2. **predict.py**: Prediction script
   - Contains the inference logic
   - Loads the model and processes images
   - Returns classification results

## Usage:

The model will be loaded and used by the classification API endpoints to analyze uploaded images and generate trait scores.

## Note:

Make sure to add large `.pth` files to `.gitignore` to avoid committing them to version control.
