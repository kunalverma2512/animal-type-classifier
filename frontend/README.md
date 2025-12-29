# 🐄 Animal Type Classifier - Frontend

**Modern React frontend** with multilingual support and responsive design for cattle classification.

---

## 📋 Overview

Frontend application providing:
- **Modern UI/UX** with React 19 and Tailwind CSS 4
- **22 Indian Languages** with complete i18n support
- **Responsive Design** optimized for mobile and desktop
- **Interactive Charts** for result visualization
- **Image Upload** with preview and validation
- **Excel Export** for classification reports
- **Archive Management** for past classifications

---

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── pages/                     # Page components
│   │   ├── Home.jsx              # Landing page
│   │   ├── Classify.jsx          # Classification form
│   │   ├── Results.jsx           # Results display
│   │   ├── Archive.jsx           # Past classifications
│   │   ├── About.jsx             # About page
│   │   ├── Contact.jsx           # Contact page
│   │   └── LivenessCheck.jsx     # Liveness detection
│   │
│   ├── components/                # Reusable components
│   │   ├── Navbar.jsx            # Navigation bar
│   │   ├── Footer.jsx            # Footer
│   │   ├── LanguageSwitcher.jsx  # Language selector
│   │   └── TraitCard.jsx         # Trait display card
│   │
│   ├── i18n/                      # Internationalization
│   │   ├── i18n.js               # i18next configuration
│   │   └── locales/              # Translation files (22 languages)
│   │       ├── en.json           # English
│   │       ├── hi.json           # Hindi
│   │       ├── ta.json           # Tamil
│   │       └── ...               # 19 more languages
│   │
│   ├── services/                  # API communication
│   │   └── api.js                # Axios configuration
│   │
│   ├── App.jsx                    # Main app component
│   └── main.jsx                   # Application entry point
│
├── public/                        # Static assets
│   ├── images/                    # Images
│   └── locales/                   # Language files (public)
│
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── package.json                   # Dependencies
├── tailwind.config.js             # Tailwind configuration
├── vite.config.js                 # Vite configuration
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ 
- **npm** or **yarn**

### Installation

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env if needed (defaults to localhost:8000)

# Start development server
npm run dev
```

**Application runs at:** http://localhost:5173

---

## 📦 Dependencies

### Core
```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "react-router-dom": "^7.9.6",
  "vite": "^7.2.4"
}
```

### UI & Styling
```json
{
  "tailwindcss": "^4.1.17",
  "framer-motion": "^12.23.25",
  "@tailwindcss/vite": "^4.1.17",
  "@tsparticles/engine": "^3.8.0",
  "@tsparticles/react": "^3.0.0"
}
```

### Internationalization
```json
{
  "i18next": "^25.7.2",
  "react-i18next": "^16.4.0",
  "i18next-browser-languagedetector": "^8.2.0"
}
```

### Utilities & Extras
```json
{
  "axios": "^1.13.2",
  "react-icons": "^5.5.0",
  "file-saver": "^2.0.5",
  "xlsx": "^0.18.5"
}
```


```

---

## 🌍 Supported Languages (22)

Complete UI translation for all Indian languages:

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `hi` | Hindi | हिंदी |
| `ta` | Tamil | தமிழ் |
| `te` | Telugu | తెలుగు |
| `kn` | Kannada | ಕನ್ನಡ |
| `ml` | Malayalam | മലയാളം |
| `mr` | Marathi | मराठी |
| `gu` | Gujarati | ગુજરાતી |
| `bn` | Bengali | বাংলা |
| `pa` | Punjabi | ਪੰਜਾਬੀ |
| `or` | Odia | ଓଡ଼ିଆ |
| `as` | Assamese | অসমীয়া |
| `ur` | Urdu | اردو |
| `ks` | Kashmiri | کٲشُر |
| `kok` | Konkani | कोंकणी |
| `ne` | Nepali | नेपाली |
| `brx` | Bodo | बड़ो |
| `doi` | Dogri | डोगरी |
| `mai` | Maithili | मैथिली |
| `mni` | Manipuri | মৈতৈলোন্ |
| `sat` | Santali | ᱥᱟᱱᱛᱟᱲᱤ |
| `sd` | Sindhi | سنڌي |

---

## 🎨 Features

### Classification Workflow

1. **Animal Information Form**
   - Tag Number (with pattern validation)
   - Breed selection (13 Indian breeds)
   - Date of Birth (date picker)
   - Lactation Number
   - Date of Calving
   - Village & Farmer Name

2. **Image Upload** (5 views required)
   - 📸 Rear View
   - 📸 Side View
   - 📸 Top View
   - 📸 Udder View
   - 📸 Side-Udder View
   - Live preview before upload
   - File size validation (max 5MB)
   - Format validation (JPG, PNG, JPEG, WEBP)

3. **Real-time Processing**
   - Loading indicator during classification
   - Status updates from backend
   - Error handling with user-friendly messages

4. **Results Display**
   - Official 20-trait scoring table
   - Radar chart for category scores
   - Overall grade badge
   - Measurement details (pixels/cm)
   - Excel export functionality

5. **Archive Management**
   - List of past classifications
   - Search and filter
   - View detailed results
   - Re-export to Excel

### UI Components

#### Language Switcher
```jsx
// Accessible from navbar
<LanguageSwitcher />
// Auto-detects browser language
// Persists selection to localStorage
```

#### Trait Visualization
```jsx
<TraitCard 
  trait="Stature"
  score={7}
  measurement={138.5}
  unit="cm"
/>
```

#### Results Chart
```jsx
// Radar chart showing category scores
<RadarChart data={categoryScores} />
```

---

## 🔐 Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Production
# VITE_API_BASE_URL=https://your-backend.onrender.com
```

**Note:** Vite requires `VITE_` prefix for environment variables.

---

## 🛠️ Development

### Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run linting
npm run lint
```

### Development Server

```bash
npm run dev
```

**Opens at:** http://localhost:5173  
**Features:**
- ⚡ Hot Module Replacement (HMR)
- 🔥 Fast refresh
- 📝 Source maps for debugging

### Building for Production

```bash
npm run build
```

**Output:** `dist/` folder  
**Optimizations:**
- Code splitting
- Tree shaking
- Minification
- Asset optimization

### Preview Production Build

```bash
npm run preview
```

Tests production build locally before deployment.

---

## 📁 Key Files

### Configuration

#### tailwind.config.js
```javascript
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#10b981',    // Green
        secondary: '#3b82f6',  // Blue
        // Custom color palette
      }
    }
  }
}
```

#### vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    port: 5173,
    host: true
  }
})
```

### API Service

#### src/services/api.js
```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const classifyAnimal = async (formData) => {
  const response = await api.post('/classification/classify', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
```

---

## 🚀 Deployment

### Vercel Deployment (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**Configuration:** `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Environment Variables (Vercel Dashboard):**
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### Other Platforms

#### Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

#### GitHub Pages
```bash
npm run build
# Use gh-pages or GitHub Actions
```

---

## 🎨 Styling Guide

### Tailwind CSS

**Primary Colors:**
```jsx
<div className="bg-green-500 text-white">Primary</div>
<div className="bg-blue-500 text-white">Secondary</div>
```

**Responsive Design:**
```jsx
<div className="text-sm md:text-base lg:text-lg">
  Responsive text
</div>
```

**Common Patterns:**
```jsx
// Card
<div className="bg-white rounded-lg shadow-md p-6">
  Card content
</div>

// Button
<button className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg transition">
  Click me
</button>

// Input
<input className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-500" />
```

---

## 🐛 Troubleshooting

### Vite Build Errors
```
Error: Cannot find module
```
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### API Connection Failed
```
Error: Network Error
```
**Solution:**
- Check `VITE_API_BASE_URL` in `.env`
- Ensure backend is running
- Check CORS settings in backend

### Translation Not Showing
```
Key 'some.key' not found
```
**Solution:**
- Check translation key exists in `src/i18n/locales/{lang}.json`
- Verify i18n is properly initialized
- Clear browser cache

### Build Size Too Large
**Solution:**
```bash
# Analyze bundle
npm run build -- --mode analysis

# Use lazy loading for routes
const Classify = lazy(() => import('./pages/Classify'));
```

---

## 🤝 Contributing

When contributing to frontend:

1. Follow **React best practices**
2. Maintain **component reusability**
3. Keep **translations in sync** across all 22 languages
4. Test **responsiveness** on mobile and desktop
5. Ensure **accessibility** (ARIA labels, keyboard navigation)

---

## 📊 Performance

### Lighthouse Scores (Target)

- **Performance:** 90+
- **Accessibility:** 100
- **Best Practices:** 95+
- **SEO:** 100

### Optimization Tips

```javascript
// Code splitting
const Results = lazy(() => import('./pages/Results'));

// Image optimization
<img loading="lazy" src={imageSrc} alt="..." />

// Memoization
const MemoizedComponent = React.memo(Component);
```

---

## 📄 License

MIT License - Educational/Government Use

---

## 🔗 Related

- **Main README:** [../README.md](../README.md)
- **Backend README:** [../backend/README.md](../backend/README.md)
- **Deployment Guide:** [../DEPLOYMENT.md](../DEPLOYMENT.md)

---

**Made with ❤️ for SIH 2025 | React 19 + Vite 7 + Tailwind CSS 4**
