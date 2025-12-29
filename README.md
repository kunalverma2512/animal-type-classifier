# 🐄 Animal Type Classifier - Official Government Format

> **AI-Powered Cattle Type Classification System** with ML-based trait analysis and official government format compliance (Annex II - 20 Traits)

<img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+"/> <img src="https://img.shields.io/badge/React-19-61DAFB.svg" alt="React 19"/> <img src="https://img.shields.io/badge/FastAPI-Modern-009688.svg" alt="FastAPI"/> <img src="https://img.shields.io/badge/MongoDB-Database-47A248.svg" alt="MongoDB"/> <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/>

**Smart India Hackathon 2025** | Government of India Initiative

---

## 🌟 Overview

An intelligent cattle type classification system that analyzes animal traits using **YOLOv8 pose estimation models** and provides official government-compliant scoring across 20 standardized traits. The system processes multiple view angles (rear, side, top, udder) to extract precise body measurements and scores.

### Key Highlights

- 🎯 **Official Government Compliance**: Exact implementation of Type Evaluation Format (Annex II)
- 🤖 **ML-Powered Analysis**: YOLOv8 pose estimation models for 5 different view angles
- 📊 **20-Trait Comprehensive Scoring**: Automated trait evaluation on 1-9 scale
- 📥 **Smart Model Management**: Automatic download from Hugging Face with intelligent caching
- 📱 **Modern, Responsive UI**: Built with React 19 and Tailwind CSS 4
- 💾 **Robust Data Storage**: MongoDB with archive and Excel export
- 🚀 **Production Ready**: Deployment-ready for Render/Vercel

---

## 🏗️ Architecture

### Tech Stack

#### Frontend
- **React 19** + **Vite 7** - Modern, fast development
- **React Router v7** - Client-side routing
- **Tailwind CSS 4** - Utility-first styling
- **Framer Motion 12** - Smooth animations
- **Axios** - HTTP client for API calls

#### Backend
- **Python 3.9+** - Core language
- **FastAPI** - Modern, async-first API framework
- **MongoDB** - NoSQL database for classifications
- **Ultralytics YOLOv8** - Pose estimation ML models (5 models, ~40MB each)
- **OpenCV** - Image processing
- **Requests** - HTTP downloads from Hugging Face

#### ML Models (Auto-downloaded from Hugging Face)
- **Rear View Model** - Rump width, leg analysis
- **Side View Model** - Body measurements, leg angles
- **Top View Model** - Chest width analysis
- **Udder View Model** - Teat placement and measurements
- **Side-Udder Model** - Udder attachment and depth

---

## 📁 Project Structure

```
animal-type-classifier/
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/              # Page components (Home, Classify, Results, etc.)
│   │   ├── services/           # API service layer
│   │   └── main.jsx            # Application entry point
│   ├── .env.example            # Environment variables template
│   ├── package.json            # Dependencies
│   └── README.md               # Frontend-specific docs
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── api/routes/         # API endpoints
│   │   ├── core/               # Configuration & database
│   │   ├── models/             # Pydantic schemas & trait definitions
│   │   └── services/           # Business logic (AI service)
│   ├── ml_models/              # ML model integration
│   │   ├── model_downloader.py         # Auto-downloads from Hugging Face
│   │   ├── rear_view_integration.py    # Rear view processing
│   │   ├── side_view_integration.py    # Side view processing
│   │   ├── top_view_integration.py     # Top view processing
│   │   ├── udder_view_integration.py   # Udder view processing
│   │   └── side_udder_integration.py   # Side-udder processing
│   ├── .env.example            # Environment variables template
│   ├── requirements.txt        # Python dependencies
│   ├── render.yaml             # Render deployment config
│   └── README.md               # Backend-specific docs
│
├── DEPLOYMENT.md               # Deployment guide (Render + Vercel)
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **MongoDB** (local or Atlas)
- **Git** for cloning

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/animal-type-classifier.git
cd animal-type-classifier
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate (Windows: venv\Scripts\activate)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your MongoDB URL

# Start server
uvicorn app.main:app --reload
```

**Backend runs at:** http://localhost:8000  
**API Docs:** http://localhost:8000/api/v1/docs

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment (optional - defaults to localhost:8000)
cp .env.example .env

# Start development server
npm run dev
```

**Frontend runs at:** http://localhost:5173

---

## 🎯 Official 20 Traits Classification

### Section 1: STRENGTH (5 traits)
1. **Stature** - Overall height measurement
2. **Heart Girth** - Chest circumference
3. **Body Length** - Shoulder to hip distance
4. **Body Depth** - Chest to abdomen depth
5. **Angularity** - Body angle measurements

### Section 2: RUMP (2 traits)
6. **Rump Angle** - Hip to pin bone slope
7. **Rump Width** - Pin bone spacing

### Section 3: FEET AND LEG (3 traits)
8. **Rear Legs Set** - Hock to hoof angle
9. **Rear Legs Rear View** - Leg alignment (toe-in/out)
10. **Foot Angle** - Hoof angle

### Section 4: UDDER (9 traits)
11. **Fore Udder Attachment** - Front attachment strength
12. **Rear Udder Height** - Attachment height
13. **Central Ligament** - Udder cleft definition
14. **Udder Depth** - Distance from hock
15. **Front Teat Placement** - Spacing between front teats
16. **Teat Length** - Average teat length
17. **Rear Teat Placement** - Spacing between rear teats
18. **Rear Udder Width** - Width measurement
19. **Teat Thickness** - Teat diameter

### Section 5: GENERAL (1 trait)
20. **Body Condition Score** - Overall body condition (1-9 scale)

---

## 📖 Usage Guide

### Classification Workflow

1. **Navigate** to http://localhost:5173
2. **Go to Classify** page
3. **Fill Animal Information**:
   - Tag Number
   - Breed (Gir, Sahiwal, Red Sindhi, etc.)
   - Date of Birth
   - Lactation Number
   - Date of Calving
   - Village Name
   - Farmer Name

4. **Upload 5 Required Images**:
   - 📸 Rear View
   - 📸 Side View
   - 📸 Top View
   - 📸 Udder View
   - 📸 Side-Udder View

5. **Submit for Classification**
   - First request: ~40-60 seconds (downloads models from Hugging Face)
   - Subsequent: ~3-5 seconds (uses cached models)

6. **View Detailed Results**:
   - Official 20-trait scoring
   - Category scores with radar chart
   - Measurements in pixels/cm
   - Overall grade (Excellent/Good/Average/Below Average)

7. **Export & Archive**:
   - Download Excel report
   - Save to archive for future reference
   - View past classifications

---

## 🤖 ML Model Details

### Model Management

Models are **automatically downloaded** from Hugging Face on first use:

```
https://huggingface.co/Kunalv/animal-type-classifier-models
```

**5 Models** (~40MB each, 200MB total):
- `rear_view_model.pt` - Rump and leg keypoints
- `side_view_model_v2.pt` - Body measurements
- `top_view_model.pt` - Chest width
- `udder_view_model.pt` - Teat analysis
- `cattle_side_udder.pt` - Udder attachment

**Smart Caching**:
- Downloaded once, cached locally
- Validated for completeness
- Automatic retry on failure
- Thread-safe for concurrent requests

### Model Architecture

All models use **YOLOv8 Pose Estimation**:
- Detects keypoints on cattle anatomy
- Calculates measurements (distances & angles)
- Scores traits on 1-9 scale
- Processes at 640x640 resolution

---

## 🔐 Environment Variables

### Backend (.env)

```env
# MongoDB Connection
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=animal_classifier

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB

# CORS - Frontend URLs
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional: Gemini AI (for future enhancements)
GEMINI_API_KEY=your_gemini_api_key_here
```

### Frontend (.env)

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📚 API Documentation

Interactive Swagger docs: **http://localhost:8000/api/v1/docs**

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/classification/classify` | POST | Complete classification with images |
| `/api/v1/classification/archive` | GET | List archived classifications |
| `/api/v1/classification/archive/{id}` | GET | Get specific archived result |
| `/health` | GET | Health check |

**See [backend/README.md](backend/README.md) for detailed API documentation.**

---

## 🚀 Deployment

### Production Deployment

**Backend:** Render (Free tier compatible)  
**Frontend:** Vercel (Free tier recommended)  
**Database:** MongoDB Atlas (Free tier - M0)

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.**

### Quick Deploy

#### Backend to Render
```bash
# Push to GitHub
git push origin main

# Connect to Render dashboard
# Set environment variables
# Deploy automatically
```

#### Frontend to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

---

## 🛠️ Development

### Frontend Commands

```bash
npm run dev          # Development server (http://localhost:5173)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Commands

```bash
uvicorn app.main:app --reload   # Development server with hot reload
python -m pytest                # Run tests (if available)
python -c "from ml_models.model_downloader import verify_all_models; print(verify_all_models())"  # Check model status
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

**MIT License** - Educational/Government Use

This project is developed for Smart India Hackathon 2025 and government cattle classification purposes.

---

## 👥 Team

**SIH 2025 Team**  
Developed for Smart India Hackathon 2025

---

## 🙏 Acknowledgments

- **Official Government Type Evaluation Format** (Annex II)
- **Ultralytics YOLOv8** - Pose estimation models
- **Hugging Face** - Model hosting
- **FastAPI & React** - Modern web frameworks
- **MongoDB Atlas** - Database hosting

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review API docs at http://localhost:8000/api/v1/docs

---

**⭐ Star this repo if you find it helpful!**

**Made with ❤️ for Smart India Hackathon 2025 | Government of India**
