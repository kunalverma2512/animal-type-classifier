# 🐄 Animal Type Classifier - Backend API

**FastAPI-powered backend** with ML-based trait analysis using YOLOv8 pose estimation models.

---

## 📋 Overview

Backend service for cattle type classification providing:
- **5 ML Models** (YOLOv8 pose estimation) processing different view angles
- **Automatic model downloads** from Hugging Face with intelligent caching
- **20-trait evaluation** following official government format (Annex II)
- **MongoDB storage** for classifications and archive
- **RESTful API** with FastAPI and automatic documentation
- **Production-ready** deployment configuration for Render

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                          # FastAPI application entry
│   ├── api/
│   │   └── routes/
│   │       └── classification.py        # Classification endpoints
│   ├── core/
│   │   ├── config.py                    # Settings & environment
│   │   └── database.py                  # MongoDB connection
│   ├── models/
│   │   ├── schemas.py                   # Pydantic models
│   │   └── trait_definitions.py         # Official 20 traits definition
│   └── services/
│       ├── ai_service.py                # ML model orchestration
│       └── status_store.py              # Processing status tracking
│
├── ml_models/                            # ML integration modules
│   ├── model_downloader.py              # Hugging Face auto-download
│   ├── rear_view_integration.py         # Rump & leg analysis
│   ├── side_view_integration.py         # Body measurements
│   ├── top_view_integration.py          # Chest width
│   ├── udder_view_integration.py        # Teat measurements
│   ├── side_udder_integration.py        # Udder attachment
│   └── bcs_integration.py               # Body condition score
│
├── uploads/                              # Image storage (ephemeral)
├── .env                                  # Environment variables
├── .env.example                          # Environment template
├── requirements.txt                      # Python dependencies
├── render.yaml                           # Render deployment config
└── README.md                             # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **MongoDB** (local or MongoDB Atlas)
- **pip** for package management

### Installation

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your MongoDB connection string

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server runs at:** http://localhost:8000  
**API Documentation:** http://localhost:8000/api/v1/docs  
**Health Check:** http://localhost:8000/health

---

## 📦 Dependencies

### Core Framework
```
fastapi[standard]       # Modern async web framework
uvicorn                 # ASGI server
python-dotenv           # Environment variables
pydantic-settings       # Settings management
```

### Database
```
motor                   # Async MongoDB driver
pymongo                 # MongoDB support
```

### ML & Image Processing
```
ultralytics             # YOLOv8 models
opencv-python-headless  # Image processing (server-optimized)
requests                # HTTP downloads from Hugging Face
Pillow                  # Image handling
```

### Optional
```
google-generativeai     # Gemini AI (for future enhancements)
```

---

## 🤖 ML Models

### Model Management

Models are **automatically downloaded** from Hugging Face on first use:

```
Repository: https://huggingface.co/Kunalv/animal-type-classifier-models
```

**5 YOLOv8 Pose Models** (~40MB each):

| Model | Purpose | Keypoints | Traits Extracted |
|-------|---------|-----------|------------------|
| `rear_view_model.pt` | Rump & legs | 8 | Rump width, Rear legs rear view |
| `side_view_model_v2.pt` | Body measurements | 14 | Stature, Heart girth, Body length, Body depth, Rump angle, Rear legs set, Foot angle, Angularity |
| `top_view_model.pt` | Chest analysis | 8 | Chest width |
| `udder_view_model.pt` | Teat analysis | 8 | Front/rear teat placement, Teat length/thickness, Rear udder width/height |
| `cattle_side_udder.pt` | Udder attachment | 5 | Fore udder attachment, Udder depth, Central ligament |

### Smart Caching System

```python
# First request (no cached models)
📥 Downloading model: rear_view_model.pt
   Progress: 10.0 MB / 40.3 MB (24.8%)
   ...
✓ Successfully downloaded: rear_view_model.pt (40.3 MB)

# Subsequent requests
✓ Using cached model: rear_view_model.pt (40.3 MB)  # Instant!
```

**Features:**
- ✅ Download on first use
- ✅ Validate file size (prevents corrupted files)
- ✅ Retry logic with exponential backoff
- ✅ Thread-safe (concurrent requests)
- ✅ Automatic fallback to urllib if requests unavailable

---

## 🎯 Official 20 Traits

Implementation follows **Annex II - Official Type Evaluation Format**:

### Section 1: STRENGTH (5 traits)
1. Stature
2. Heart Girth  
3. Body Length
4. Body Depth
5. Angularity

### Section 2: RUMP (2 traits)
6. Rump Angle
7. Rump Width

### Section 3: FEET AND LEG (3 traits)
8. Rear Legs Set
9. Rear Legs Rear View
10. Foot Angle

### Section 4: UDDER (9 traits)
11. Fore Udder Attachment
12. Rear Udder Height
13. Central Ligament
14. Udder Depth
15. Front Teat Placement
16. Teat Length
17. Rear Teat Placement
18. Rear Udder Width
19. Teat Thickness

### Section 5: GENERAL (1 trait)
20. Body Condition Score

---

## 📚 API Endpoints

### Health & Status

```http
GET /health
```
Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Classification

#### Complete Classification
```http
POST /api/v1/classification/classify
Content-Type: multipart/form-data

# Form fields:
- animal_info: {
    "tagNumber": "ABC123",
    "animalType": "cattle",
    "breed": "Gir",
    "dateOfBirth": "2020-01-15",
    "lactationNumber": 2,
    "dateOfCalving": "2024-06-01",
    "village": "Sample Village",
    "farmerName": "John Doe"
  }
- images: [rear.jpg, side.jpg, top.jpg, udder.jpg, side_udder.jpg]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "classificationId": "677e2f3a1234567890abcdef",
    "officialFormat": {
      "villageName": "Sample Village",
      "farmerName": "John Doe",
      "animalTagNo": "ABC123",
      "classificationDate": "2025-12-29",
      "sections": {
        "Strength": [
          {
            "trait": "Stature",
            "score": 7,
            "measurement": 138.5
          },
          ...
        ],
        "Rump": [...],
        "Feet and Leg": [...],
        "Udder": [...],
        "General": [...]
      }
    },
    "categoryScores": {
      "Strength": 6.8,
      "Rump": 7.0,
      "Feet and Leg": 6.5,
      "Udder": 7.2,
      "General": 5.0
    },
    "overallScore": 6.7,
    "grade": "Good",
    "totalTraits": 20,
    "processed": true
  }
}
```

#### Get Archive
```http
GET /api/v1/classification/archive?limit=10&skip=0
```

Returns list of past classifications.

#### Get Specific Result
```http
GET /api/v1/classification/archive/{id}
```

Returns detailed results for a specific classification ID.

**Interactive API Docs:** http://localhost:8000/api/v1/docs

---

## 🔐 Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# ===================================
# Backend Environment Variables
# ===================================

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# MongoDB Database
# Get connection string from MongoDB Atlas or use local MongoDB
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=animal_classification

# Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB in bytes

# CORS - Frontend URLs allowed to access this API
# Add your frontend URLs (local dev and production)
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-frontend.vercel.app

# Optional: Gemini AI API Key (for future enhancements)
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🛠️ Development

### Running Tests

```bash
# Check model status
python -c "from ml_models.model_downloader import verify_all_models; import json; print(json.dumps(verify_all_models(), indent=2))"

# Test individual model integration
python -m ml_models.rear_view_integration ml_models/test_images/1_rear_view.jpg
python -m ml_models.side_view_integration ml_models/test_images/2_side_view.jpg
```

### Hot Reload Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Changes to Python files automatically reload the server.

### Database Management

**MongoDB Shell:**
```bash
# Connect to MongoDB
mongosh "your_mongodb_connection_string"

# View classifications
use animal_classification
db.classifications.find().pretty()
```

---

## 🚀 Deployment

### Render Deployment

**Configuration:** `render.yaml`

```yaml
services:
  - type: web
    name: animal-classifier-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false  # Set in Render dashboard
      - key: DATABASE_NAME
        value: animal_classifier
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.vercel.app
      - key: UPLOAD_DIR
        value: /tmp/uploads
```

**Environment Variables to Set in Render:**
- `MONGODB_URL` - Your MongoDB Atlas connection string
- `DATABASE_NAME` - Database name (e.g., `animal_classifier`)
- `ALLOWED_ORIGINS` - Frontend URL (Vercel deployment)
- `UPLOAD_DIR` - Use `/tmp/uploads` for ephemeral storage

**First Request Behavior:**
- Models download from Hugging Face (~40-60 seconds)
- Subsequent requests use cached models (~3-5 seconds)
- On Render free tier, models re-download after service sleeps

---

## ⚙️ Configuration

### CORS Settings

Edit `ALLOWED_ORIGINS` in `.env`:

```env
# Development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Production (add your frontend URL)
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### Upload Directory

**Local Development:**
```env
UPLOAD_DIR=uploads  # Creates folder in backend/
```

**Production (Render):**
```env
UPLOAD_DIR=/tmp/uploads  # Uses temporary storage
```

---

## 🐛 Troubleshooting

### MongoDB Connection Failed
```
Error: pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**
- Verify `MONGODB_URL` is correct
- Check MongoDB Atlas whitelist (allow 0.0.0.0/0 or Render IPs)
- Ensure database user has proper permissions

### Model Download Fails
```
Error: Failed to download rear_view_model.pt after 3 attempts
```

**Solutions:**
- Check internet connection
- Verify Hugging Face is accessible
- Models will retry with exponential backoff
- Check logs for specific error

### Import Errors
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### CORS Errors
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Solution:**
Add frontend URL to `ALLOWED_ORIGINS` in `.env`

---

## 📊 Monitoring

### Logs

**Development:**
Logs appear directly in terminal with uvicorn.

**Production (Render):**
View logs in Render dashboard under "Logs" tab.

**Key log messages:**
```
✓ Using cached model: rear_view_model.pt (40.3 MB)
✓ Side view model processed successfully
  Extracted 8 traits
```

---

## 🤝 Contributing

When contributing to backend:

1. Follow **FastAPI best practices**
2. Maintain **type hints** for all functions
3. Update **Pydantic schemas** for API changes
4. Keep **trait_definitions.py** aligned with official format
5. Test **model integration** with sample images

---

## 📄 License

MIT License - Educational/Government Use

---

## 🔗 Related

- **Main README:** [../README.md](../README.md)
- **Frontend README:** [../frontend/README.md](../frontend/README.md)
- **Deployment Guide:** [../DEPLOYMENT.md](../DEPLOYMENT.md)

---

**Made with ❤️ for SIH 2025 | FastAPI + YOLOv8 + MongoDB**
