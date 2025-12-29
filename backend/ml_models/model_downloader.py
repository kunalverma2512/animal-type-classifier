"""
Model Downloader Utility
Downloads and caches ML models from Hugging Face
"""
import os
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional
import threading

# Configure logging
logger = logging.getLogger(__name__)

# Thread lock for safe concurrent downloads
_download_lock = threading.Lock()

# Directory where models are stored - use weights directory
ML_MODELS_DIR = Path(__file__).parent / "weights"

# Hugging Face model URLs
MODEL_URLS = {
    "rear_view_model.pt": "https://huggingface.co/Kunalv/animal-type-classifier-models/resolve/main/rear_view_model.pt",
    "side_view_model_v2.pt": "https://huggingface.co/Kunalv/animal-type-classifier-models/resolve/main/side_view_model_v2.pt",
    "top_view_model.pt": "https://huggingface.co/Kunalv/animal-type-classifier-models/resolve/main/top_view_model.pt",
    "cattle_side_udder.pt": "https://huggingface.co/Kunalv/animal-type-classifier-models/resolve/main/cattle_side_udder.pt",
    "udder_view_model.pt": "https://huggingface.co/Kunalv/animal-type-classifier-models/resolve/main/udder_view_model.pt"
}

# Minimum expected file sizes (in bytes) to validate downloads
# YOLOv8 pose models are typically ~40MB
MIN_MODEL_SIZE = 10 * 1024 * 1024  # 10 MB


def get_model_path(model_filename: str) -> Optional[Path]:
    """
    Get the local path to a model, downloading it if necessary.
    
    Args:
        model_filename: Name of the model file (e.g., "rear_view_model.pt")
        
    Returns:
        Path object pointing to the local model file, or None if download fails
    """
    if model_filename not in MODEL_URLS:
        logger.error(f"Unknown model: {model_filename}")
        logger.error(f"Available models: {', '.join(MODEL_URLS.keys())}")
        return None
    
    # Ensure weights directory exists
    ML_MODELS_DIR.mkdir(exist_ok=True)
    
    model_path = ML_MODELS_DIR / model_filename
    
    # Check if model already exists and is valid
    if model_path.exists():
        file_size = model_path.stat().st_size
        if file_size >= MIN_MODEL_SIZE:
            logger.info(f"Using cached model: {model_filename} ({file_size / (1024*1024):.1f} MB)")
            return model_path
        else:
            logger.warning(f"Cached model too small ({file_size} bytes), re-downloading...")
            model_path.unlink()  # Delete corrupted/incomplete file
    
    # Model doesn't exist or is invalid - download it
    return _download_model(model_filename)


def _download_model(model_filename: str, max_retries: int = 3) -> Optional[Path]:
    """
    Download a model from Hugging Face with retry logic.
    
    Args:
        model_filename: Name of the model file
        max_retries: Maximum number of download attempts
        
    Returns:
        Path to the downloaded model, or None if all attempts fail
    """
    url = MODEL_URLS[model_filename]
    model_path = ML_MODELS_DIR / model_filename
    temp_path = ML_MODELS_DIR / f"{model_filename}.tmp"
    
    # Use thread lock to prevent concurrent downloads of the same model
    with _download_lock:
        # Double-check if another thread already downloaded it
        if model_path.exists() and model_path.stat().st_size >= MIN_MODEL_SIZE:
            logger.info(f"Model already downloaded by another process: {model_filename}")
            return model_path
        
        logger.info(f"Downloading model: {model_filename}")
        logger.info(f"Source: {url}")
        logger.info(f"Target: {model_path}")
        
        for attempt in range(1, max_retries + 1):
            try:
                # Try using requests library first (more robust)
                try:
                    import requests
                    response = requests.get(url, stream=True, timeout=60)
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Log progress every 5MB
                                if downloaded % (5 * 1024 * 1024) < 8192:
                                    if total_size > 0:
                                        percent = (downloaded / total_size) * 100
                                        logger.debug(f"Progress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({percent:.1f}%)")
                                    else:
                                        logger.debug(f"Downloaded: {downloaded / (1024*1024):.1f} MB")
                
                except ImportError:
                    # Fallback to urllib if requests is not available
                    print("   Using urllib (requests not available)")
                    import urllib.request
                    
                    with urllib.request.urlopen(url, timeout=60) as response:
                        total_size = int(response.headers.get('Content-Length', 0))
                        downloaded = 0
                        
                        with open(temp_path, 'wb') as f:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Log progress every 5MB
                                if downloaded % (5 * 1024 * 1024) < 8192:
                                    if total_size > 0:
                                        percent = (downloaded / total_size) * 100
                                        print(f"   Progress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({percent:.1f}%)")
                                    else:
                                        print(f"   Downloaded: {downloaded / (1024*1024):.1f} MB")
                
                # Validate download
                if not temp_path.exists():
                    raise RuntimeError("Download completed but file not found")
                
                file_size = temp_path.stat().st_size
                if file_size < MIN_MODEL_SIZE:
                    raise RuntimeError(f"Downloaded file too small: {file_size} bytes (expected > {MIN_MODEL_SIZE})")
                
                # Move to final location
                temp_path.rename(model_path)
                
                logger.info(f"Successfully downloaded: {model_filename} ({file_size / (1024*1024):.1f} MB)")
                return model_path
                
            except Exception as e:
                logger.error(f"Download attempt {attempt}/{max_retries} failed: {str(e)}")
                logger.exception("Full traceback:")
                
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
                
                # Retry with exponential backoff
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 2, 4, 8 seconds
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to download {model_filename} after {max_retries} attempts")
                    return None
        
        return None


def verify_all_models() -> dict:
    """
    Check status of all models (for debugging/monitoring).
    
    Returns:
        Dictionary with model status information
    """
    status = {}
    
    for model_filename in MODEL_URLS.keys():
        model_path = ML_MODELS_DIR / model_filename
        
        if model_path.exists():
            file_size = model_path.stat().st_size
            status[model_filename] = {
                'exists': True,
                'size_mb': round(file_size / (1024*1024), 2),
                'valid': file_size >= MIN_MODEL_SIZE
            }
        else:
            status[model_filename] = {
                'exists': False,
                'size_mb': 0,
                'valid': False
            }
    
    return status


if __name__ == "__main__":
    # Test the downloader
    print("=" * 60)
    print("Model Downloader Test")
    print("=" * 60)
    
    print("\nChecking model status...")
    status = verify_all_models()
    for model_name, info in status.items():
        if info['exists']:
            print(f"  ✓ {model_name}: {info['size_mb']} MB")
        else:
            print(f"  ✗ {model_name}: Not downloaded")
    
    print("\nTesting download of rear_view_model.pt...")
    model_path = get_model_path("rear_view_model.pt")
    
    if model_path:
        print(f"\n✓ Test successful! Model at: {model_path}")
    else:
        print("\n❌ Test failed!")
