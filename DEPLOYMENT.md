# Deployment Guide

This guide will help you deploy the Animal Type Classifier to production.

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub account
- Vercel account (sign up at vercel.com)

### Steps

1. **Push code to GitHub**
   ```bash
   cd frontend
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Vite configuration
   
3. **Configure Environment Variables**
   - In Vercel project settings → Environment Variables
   - Add: `VITE_API_BASE_URL` = `https://your-backend-url.onrender.com`
   - Click "Save"

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Copy your frontend URL (e.g., `https://animal-classifier.vercel.app`)

---

## Backend Deployment (Render)

### Prerequisites
- MongoDB Atlas account (free tier available)
- Render account (sign up at render.com)

### Step 1: Setup MongoDB Atlas

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create database user (username/password)
4. Whitelist all IPs: `0.0.0.0/0` (for Render access)
5. Get connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 2: Deploy to Render

1. **Push code to GitHub**
   ```bash
   cd backend
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to [render.com](https://render.com) and sign in
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `backend` folder as root directory

3. **Configure Service**
   - **Name**: `animal-classifier-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   In Render dashboard, add these environment variables:
   
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=animal_classifier
   UPLOAD_DIR=/tmp/uploads
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:5173
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes for first deploy)
   - Copy your backend URL (e.g., `https://animal-classifier-api.onrender.com`)

### Step 3: Update Frontend with Backend URL

1. Go back to Vercel
2. Update environment variable:
   - `VITE_API_BASE_URL` = `https://animal-classifier-api.onrender.com`
3. Redeploy frontend

### Step 4: Update Backend CORS

1. In Render, update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://animal-classifier.vercel.app,http://localhost:5173
   ```
   (Replace with your actual Vercel URL)
2. Save and redeploy

---

## Important Notes

### File Storage
- Render uses **ephemeral storage** - uploaded files in `/tmp` are deleted on restart
- For production, consider using:
  - AWS S3
  - Cloudinary
  - Or store files in MongoDB GridFS

### ML Models
- Ensure all `.pt` model files are committed to Git
- They will be deployed with your code
- Total size should be under 500MB for free Render tier

### Database
- MongoDB Atlas free tier: 512MB storage
- Sufficient for testing and small-scale production

### Monitoring
- **Render**: Check logs in dashboard
- **Vercel**: Check deployment logs and analytics

---

## Testing Deployment

1. Visit your frontend URL
2. Try creating a new classification
3. Upload test images from `backend/ml_models/test_images/`
4. Verify results display correctly
5. Check archive page

---

## Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_BASE_URL` in Vercel
- Check CORS settings in Render
- Ensure backend is running (Render dashboard)

### Backend crashes
- Check Render logs
- Verify MongoDB connection string
- Check if ML models are loaded

### Images not uploading
- Check file size limits
- Verify upload directory is `/tmp/uploads` on Render

---

## Cost Estimate

- **Vercel**: Free (Hobby plan)
- **Render**: Free tier available (may sleep after 15 min of inactivity)
- **MongoDB Atlas**: Free tier (512MB)

**Tip**: For production with consistent uptime, upgrade Render to paid plan ($7/month).
