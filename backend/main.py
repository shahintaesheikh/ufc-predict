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
    prediction_data = [
        red_stats['reach_cm'],
        red_stats['ss_landed_per_minute'],
        red_stats['ss_accuracy'],
        red_stats['ss_absorbed_per_min'],
        red_stats['ss_defence'],
        red_stats['avg_td_per_15'],
        red_stats['td_accuracy'],
        red_stats['td_defence'],
        red_stats['avg_sub_attempt_per_15'],
        blue_stats['reach_cm'],
        blue_stats['ss_landed_per_minute'],
        blue_stats['ss_accuracy'],
        blue_stats['ss_absorbed_per_min'],
        blue_stats['ss_defence'],
        blue_stats['avg_td_per_15'],
        blue_stats['td_accuracy'],
        blue_stats['td_defence'],
        blue_stats['avg_sub_attempt_per_15']
    ]

    return np.array([prediction_data])

model = xgb.XGBClassifier()
model.load_model('/shahinsheikh/ufc-predictor-web/backend/models/ufc_xgb.json')

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
    prediction_data_1 = prepare_data(red_stats, blue_stats)
    prob_1 = model.predict_proba(prediction_data_1)[0]
    # prob_1[0] = probability that position 1 (red) wins
    red_prob_from_setup1 = float(prob_1[0])

    # Setup 2: Red fighter in blue position, Blue fighter in red position (FLIPPED)
    prediction_data_2 = prepare_data(blue_stats, red_stats)
    prob_2 = model.predict_proba(prediction_data_2)[0]
    # prob_2[1] = probability that position 2 (blue) loses = probability red fighter wins
    # But since red is now in blue position: prob_2[1] = P(red loses from blue position)
    # So P(red wins) = 1 - prob_2[0]
    red_prob_from_setup2 = 1.0 - float(prob_2[0])

    # Average the two predictions to get position-unbiased estimate
    red_probability = (red_prob_from_setup1 + red_prob_from_setup2) / 2.0
    blue_probability = 1.0 - red_probability

    # Determine winner
    if red_probability > blue_probability:
        winner = "RedFighter wins"
        confidence = red_probability
    else:
        winner = "BlueFighter win"
        confidence = blue_probability

    return {
        "winner" : winner,
        "red_fighter" : request.red_fighter,
        "blue_fighter" : request.blue_fighter,
        "red_win_probability" : red_probability,
        "blue_win_probability" : blue_probability,
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
