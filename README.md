# UFC Fight Predictor 🥊

A machine learning web app that predicts UFC fight outcomes using XGBoost and fighter statistics.

**Live Demo**: https://ufc-predictor.vercel.app  
**API Docs**: https://ufc-predictor-api.onrender.com/docs

## Overview

This app predicts winners in hypothetical UFC matchups based on fighter stats like reach, striking accuracy, and takedown defense. The model is trained on 4000+ historical fights and achieves ~86% accuracy.

## Features

- **Unbiased Predictions** - Uses differential features to eliminate corner bias
- **Real-time Results** - Instant predictions with confidence scores
- **Fighter Database** - 250+ active UFC fighters with current stats
- **Responsive Design** - Works on desktop, tablet, and mobile
- **REST API** - Full API access with documentation

## Tech Stack

**Backend**
- Python, FastAPI, XGBoost, Pandas, Uvicorn

**Frontend**
- React, Vite, Axios, React-Select

**Deployment**
- Render (backend), Vercel (frontend)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Visit: http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

## API Endpoints

### GET /fighters
Returns list of all fighters
```json
{
  "fighters": ["Conor McGregor", "Khabib Nurmagomedov", ...]
}
```

### POST /predict
Predicts fight outcome

**Request:**
```json
{
  "red_fighter": "Conor McGregor",
  "blue_fighter": "Khabib Nurmagomedov"
}
```

**Response:**
```json
{
  "winner": "BlueFighter wins",
  "red_fighter": "Conor McGregor",
  "blue_fighter": "Khabib Nurmagomedov",
  "red_win_probability": 0.35,
  "blue_win_probability": 0.65,
  "confidence": 0.65
}
```

## Project Structure
```
ufc-fight-predictor/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Dependencies
│   ├── models/
│   │   └── ufc_xgb.json       # Trained model
│   └── data/
│       └── fighters.csv       # Fighter stats
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main component
│   │   ├── components/        # React components
│   │   └── services/
│   │       └── api.js         # API client
│   └── package.json
└── README.md
```

## How It Works

The model uses **differential features** to ensure fair predictions:

**Traditional (biased):**
```
Red_reach = 188cm
Blue_reach = 178cm
```

**Our approach (unbiased):**
```
reach_advantage = 188 - 178 = 10cm
```

This eliminates the historical bias where higher-ranked fighters were assigned to red corner. Swapping fighters gives symmetric, inverse probabilities.

### 9 Model Features
1. reach_advantage
2. ss_landed_advantage (strikes per minute)
3. ss_accuracy_advantage
4. ss_absorbed_advantage
5. ss_defence_advantage
6. td_per_15_advantage (takedowns)
7. td_accuracy_advantage
8. td_defence_advantage
9. sub_attempt_advantage (submissions)

## Deployment

### Backend (Render)
1. Push to GitHub
2. Create Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Frontend (Vercel)
1. Push to GitHub
2. Import project on Vercel
3. Add environment variable: `VITE_API_URL=https://your-api.onrender.com`
4. Deploy

## Model Performance

- **Accuracy**: ~66%
- **Training Data**: 4000+ fights
- **Prediction Time**: <100ms
- **Symmetric**: Swapping fighters gives consistent results

- 
## Roadmap

**Completed ✅**
- [x] Model training with differential features
- [x] FastAPI backend with logging
- [x] React frontend with responsive design
- [x] Production deployment

**Planned 📋**
- [ ] Feature importance explanations (SHAP)
- [ ] Fighter profile pages
- [ ] Prediction history tracking
- [ ] Dark mode
- [ ] Mobile app

