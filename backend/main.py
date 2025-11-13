from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import xgboost as xgb
import pandas as pd
from pydantic import BaseModel
import numpy as np

fighter_df = pd.read_csv('/Users/shahinsheikh/ufc-predictor-web/backend/data/fighter_data.csv')

class PredictionRequest(BaseModel):
    red_fighter : str
    blue_fighter : str

def get_stats(fighter_name : str):
    stats = fighter_df[fighter_df["name"]==fighter_name]

    if stats.empty:
        return None

    fighter = stats.iloc[0]

    data = {
        'reach_cm': fighter['reach_cm'],
        'ss_landed_per_minute': fighter['ss_landed_per_minute'],
        'ss_accuracy': fighter['ss_accuracy'],
        'ss_absorbed_per_min': fighter['ss_absorbed_per_min'],
        'ss_defence': fighter['ss_defence'],
        'avg_td_per_15': fighter['avg_td_per_15'],
        'td_accuracy': fighter['td_accuracy'],
        'td_defence': fighter['td_defence'],
        'avg_sub_attempt_per_15': fighter['avg_sub_attempt_per_15']
    }

    return data

#get data in features format
def prepare_data(red_stats : dict, blue_stats : dict):
    """
    Create differential-based features for prediction.
    Each feature is calculated as: Red value - Blue value
    Positive differential = Red fighter advantage
    Negative differential = Blue fighter advantage

    Note: stance and dob differentials are included to match training features.
    Since these are non-numeric, they contribute NaN values which get treated as 0 during prediction.
    """
    prediction_data = [
        red_stats['reach_cm'] - blue_stats['reach_cm'],
        np.nan,  # stance differential (non-numeric, becomes NaN then 0)
        np.nan,  # dob differential (non-numeric, becomes NaN then 0)
        red_stats['ss_landed_per_minute'] - blue_stats['ss_landed_per_minute'],
        red_stats['ss_accuracy'] - blue_stats['ss_accuracy'],
        red_stats['ss_absorbed_per_min'] - blue_stats['ss_absorbed_per_min'],
        red_stats['ss_defence'] - blue_stats['ss_defence'],
        red_stats['avg_td_per_15'] - blue_stats['avg_td_per_15'],
        red_stats['td_accuracy'] - blue_stats['td_accuracy'],
        red_stats['td_defence'] - blue_stats['td_defence'],
        red_stats['avg_sub_attempt_per_15'] - blue_stats['avg_sub_attempt_per_15']
    ]

    # Replace NaN with 0 (matching the model training pipeline)
    prediction_data = [0 if (isinstance(x, float) and np.isnan(x)) else x for x in prediction_data]

    return np.array([prediction_data])

model = xgb.XGBClassifier()
model.load_model('/Users/shahinsheikh/ufc-predictor-web/backend/models/ufc_xgb.json')

app = FastAPI()

@app.get("/fighters")
def get_fighters():
    fighter_names = fighter_df['name'].unique().tolist()

    fighter_names.sort()

    return {"fighters": fighter_names}

@app.post("/predict")
def predict(request:PredictionRequest):
    red_stats = get_stats(request.red_fighter)
    blue_stats = get_stats(request.blue_fighter)

    if red_stats is None:
        raise HTTPException(status_code=404, detail = f"Fighter '{request.red_fighter}' not found")
    if blue_stats is None:
        raise HTTPException(status_code=404, detail = f"Fighter '{request.blue_fighter}' not found")

    # Setup 1: Red fighter in red position, Blue fighter in blue position
    prediction_data = prepare_data(red_stats, blue_stats)
    proba = model.predict_proba(prediction_data)[0]
    prob_red_loses = float(proba[0])  # Class 0: Red fighter loses
    prob_red_wins = float(proba[1])   # Class 1: Red fighter wins

    # Determine winner
    if prob_red_wins > prob_red_loses:
        winner = "RedFighter wins"
        confidence = prob_red_wins
    else:
        winner = "BlueFighter wins"
        confidence = prob_red_loses

    return {
        "winner" : winner,
        "red_fighter" : request.red_fighter,
        "blue_fighter" : request.blue_fighter,
        "red_win_probability" : prob_red_wins,
        "blue_win_probability" : prob_red_loses,
        "confidence" : confidence,
    }

@app.get("/")
def read_root():
    return {"message":"UFC Fight Predictor API is running"}

#x characteristics for each fighter
#whole model has 2x features
#decision tree splits based on which data is pure
#features should be difference between red and blue fighter
#
