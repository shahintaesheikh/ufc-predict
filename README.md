# UFC Fight Predictor 🥊

A full-stack machine learning web application that predicts the outcomes of UFC fights using XGBoost and historical fighter statistics.

## 🎯 Project Overview

This application uses machine learning to predict the winner of hypothetical UFC matchups based on fighter statistics including reach, striking accuracy, takedown defense, and more. The model is trained on 4000+ historical UFC fights and uses differential features to eliminate positional bias, ensuring symmetric and fair predictions.

## ✨ Features

- **Unbiased Predictions**: Uses differential feature engineering to eliminate Red/Blue corner bias
- **Symmetric Results**: Swapping fighters produces consistent probability inversions
- **Fighter Database**: Comprehensive database of active UFC fighters with current statistics
- **RESTful API**: FastAPI-powered backend with automatic documentation
- **Production Ready**: Includes logging, environment variables, and error handling

## 🛠️ Tech Stack

### Backend
- **Python 3.x**
- **FastAPI** - Modern web framework for building APIs
- **XGBoost** - Gradient boosting machine learning model
- **Pandas** - Data manipulation and analysis
- **Uvicorn** - ASGI server

### Machine Learning
- **XGBoost Classifier** - Gradient boosting model for binary classification
- **Differential Features** - Position-independent feature engineering
- **Scikit-learn** - Model evaluation and data splitting

### Frontend (Coming Soon)
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client for API calls

## 📊 Model Performance

- **Training Accuracy**: ~86% (with differential features, position-independent)
- **Features**: 18 differential features (9 per fighter)
- **Training Data**: 4000+ historical UFC fights
- **Prediction Type**: Binary classification (Fighter A wins / Fighter B wins)

## API Docs

## 📡 API Endpoints

### `GET /`
Health check endpoint
```json
{
  "message": "UFC Fight Predictor API is running!",
  "version": "1.0"
}
```

### `GET /health`
API health status
```json
{
  "status": "healthy",
  "model_loaded": true,
  "fighters_loaded": true
}
```

### `GET /fighters`
Returns list of all available fighters
```json
{
  "fighters": [
    "Conor McGregor",
    "Khabib Nurmagomedov",
    "Israel Adesanya",
    ...
  ]
}
```

### `POST /predict`
Predicts fight outcome between two fighters

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

## 📁 Project Structure
```
ufc-fight-predictor/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── models/
│   │   ├── ufc_xgb.json       # Trained XGBoost model
│   │   ├── feature_names.txt  # Model feature list
│   │   └── labels.txt         # Label mapping
│   └── data/
│       └── fighters.csv       # Fighter statistics database
├── frontend/                   # React frontend (coming soon)
└── README.md
```

## 🧠 Model Details

### Feature Engineering

The model uses **differential features** to ensure position-independent predictions:
```python
# Instead of absolute values:
Red_reach_cm = 188
Blue_reach_cm = 178

# We use differentials:
reach_advantage = Red_reach_cm - Blue_reach_cm = 10
```

This approach eliminates the Red/Blue corner bias present in historical UFC data.

### Features Used (9 differential features)

1. **reach_advantage** - Reach difference in cm
2. **ss_landed_advantage** - Significant strikes landed per minute difference
3. **ss_accuracy_advantage** - Striking accuracy difference
4. **ss_absorbed_advantage** - Significant strikes absorbed per minute difference
5. **ss_defence_advantage** - Striking defense percentage difference
6. **td_per_15_advantage** - Average takedowns per 15 minutes difference
7. **td_accuracy_advantage** - Takedown accuracy difference
8. **td_defence_advantage** - Takedown defense difference
9. **sub_attempt_advantage** - Submission attempts per 15 minutes difference


## 📝 Logging

The API logs all requests and predictions to both console and file (`api_logs.log`). Log levels can be configured via environment variables.

Example log output:
```
2024-11-21 10:30:15 - __main__ - INFO - POST /predict - Request: Conor McGregor vs Khabib Nurmagomedov
2024-11-21 10:30:15 - __main__ - INFO - POST /predict - Result: BlueFighter wins (65.00% confidence)
```

## 🚧 Development Status

### ✅ Completed
- [x] Data collection and preprocessing
- [x] Feature engineering with differential features
- [x] XGBoost model training and evaluation
- [x] FastAPI backend with RESTful endpoints
- [x] Logging and error handling
- [x] Environment variable configuration
- [x] API documentation

### 🔄 In Progress
- [ ] React frontend development
- [ ] Frontend deployment to Vercel
- [ ] Backend deployment to Render

### 📋 Planned Features
- [ ] Fighter comparison visualization
- [ ] Prediction history tracking
- [ ] Feature importance explanations (SHAP values)
- [ ] User accounts and saved predictions

## 🤝 Contributing

This is currently a personal project, but suggestions and feedback are welcome! 

## 👤 Author

**Shahin**
- UC Santa Barbara Computer Science Student
- [GitHub](https://github.com/yourusername)
- [LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- UFC for fight statistics and data
- FastAPI documentation and community
- XGBoost development team
- UCSB Computer Science Department

