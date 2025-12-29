# Test Images for Website Testing

This folder contains 5 sample cattle images for testing the classification system.

## Upload Order (IMPORTANT!)

When testing on the website, upload the images in this **exact order**:

1. **1_rear_view.jpg** - Rear view (for BCS + rump analysis)
2. **2_side_view.jpg** - Side view (for body measurements)
3. **3_top_view.jpg** - Top view (for chest width)
4. **4_udder_view.jpg** - Udder view (for teat measurements)
5. **5_side_udder_view.jpg** - Side-udder view (for udder attachment)

## Why This Order Matters

The backend expects images in this specific sequence:
- `image_paths[0]` = Rear view
- `image_paths[1]` = Side view
- `image_paths[2]` = Top view
- `image_paths[3]` = Udder view
- `image_paths[4]` = Side-udder view

Each image is processed by its corresponding ML model to extract specific traits.

## File Naming

Files are numbered (1-5) to make it easy to select them in order during upload.

## What to Expect

After uploading and submitting:
- All 20 official traits will be analyzed using ML models
- You'll see scores (1-9 scale) for each trait
- Overall grade and milk yield prediction
- The system uses real AI instead of mock data!

## Quick Test

1. Go to the Classify page
2. Fill in animal details (tag number, breed, DOB, etc.)
3. Upload images 1-5 in order
4. Submit for classification
5. View results with AI-powered scores
