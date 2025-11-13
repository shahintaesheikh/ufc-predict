#scraping

#import libraries
import pandas as pd
import numpy as np
import xgboost as xgb
import json

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

raw = pd.read_csv('/Users/shahinsheikh/ufc-predictor-web/backend/data/UFC_Final.csv')

# map winner names to Red or Blue
def map_winner_to_color(df):
    def get_color(row):
        winner = row['Winner']
        if pd.isna(winner):
            return np.nan
        elif winner == row['RedFighter']:
            return 'Red'
        elif winner == row['BlueFighter']:
            return 'Blue'
        else:
            return np.nan

    df['Winner'] = df.apply(get_color, axis=1)
    print(raw['Winner'].value_counts())
    return df

raw = map_winner_to_color(raw)

# Create differential-based features before dropping fighter names
def create_differentials(df):
    """
    Create differential features where:
    - Positive value = Red fighter advantage
    - Negative value = Blue fighter advantage (Red disadvantage)
    Returns DataFrame with differentials and target variable
    """
    differentials = pd.DataFrame()

    # Copy relevant columns for processing
    differentials['Weight_Class'] = df['Weight_Class']
    differentials['Winner'] = df['Winner']

    # Create differentials for all numeric features (Red - Blue)
    red_cols = [col for col in df.columns if col.startswith('Red_')]

    # Map Red columns to Blue columns
    for red_col in red_cols:
        feature_name = red_col.replace('Red_', '')
        blue_col = f'Blue_{feature_name}'

        if blue_col in df.columns:
            # Only create differentials for numeric columns (skip stance, dob, etc.)
            try:
                # Attempt to subtract (will work for numeric columns)
                differentials[feature_name] = pd.to_numeric(df[red_col], errors='coerce') - pd.to_numeric(df[blue_col], errors='coerce')
            except (TypeError, ValueError):
                # Skip non-numeric columns
                continue

    return differentials

differentials = create_differentials(raw)

# Create target variable: 1 if Red wins, 0 if Red loses (Blue wins)
# We need to map from the color (Red/Blue) to the actual outcome from the fighter's perspective
def create_target(df):
    """
    Create target variable:
    - 1: Red fighter wins
    - 0: Red fighter loses (Blue wins)
    - NaN: Draw/No contest (will be dropped)
    """
    target = pd.Series(index=df.index, dtype='float64')

    for idx, winner in df['Winner'].items():
        if winner == 'Red':
            target[idx] = 1
        elif winner == 'Blue':
            target[idx] = 0
        else:
            target[idx] = np.nan

    return target

y = create_target(raw)

# Drop rows with NaN targets (draws, no contests)
valid_idx = y.notna()
x = differentials[valid_idx].copy()
y = y[valid_idx].copy()

# Drop Weight_Class and Winner columns (metadata), keep only numeric features
x.drop(columns=['Weight_Class', 'Winner'], inplace=True)

#fill nan values with average per weight class
def fill_nan(x, weight_class):
    df_filled = x.copy()
    num_cols = df_filled.select_dtypes(include = [np.number]).columns
    df_filled[num_cols] = df_filled.groupby(weight_class)[num_cols].transform(lambda x: x.fillna(x.mean()))

    remaining_na = df_filled[num_cols].isna().sum().sum()
    if remaining_na > 0:
        df_filled[num_cols] = df_filled[num_cols].fillna((df_filled[num_cols].mean()))

    return df_filled

# Re-add Weight_Class for grouping before fill_nan
weight_class = differentials[valid_idx]['Weight_Class'].copy()
x = fill_nan(x, weight_class)

x.replace(np.nan, 0, inplace = True)

x = x.select_dtypes(include=[np.number])

# Create symmetric augmented data
# For every sample (differentials A, outcome), add a flipped version (differentials -A, flipped outcome)
print(f"\nOriginal dataset size: {len(x)}")
x_flipped = -x.copy()  # Negate all differentials
y_flipped = 1 - y.copy()  # Flip outcomes (0 -> 1, 1 -> 0)

# Combine original and flipped data
x_augmented = pd.concat([x, x_flipped], ignore_index=True)
y_augmented = pd.concat([y, y_flipped], ignore_index=True)

print(f"Augmented dataset size: {len(x_augmented)}")
print(f"(Original {len(x)} + Flipped {len(x_flipped)} = {len(x_augmented)})")

# Use augmented data for training/testing split
x = x_augmented
y = y_augmented

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state = 42)

seed = 350
np.random.seed(seed)

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

#convert back to DataFrame to keep column names
x_train = pd.DataFrame(x_train_scaled, columns=x_train.columns, index=x_train.index)
x_test = pd.DataFrame(x_test_scaled, columns=x_test.columns, index=x_test.index)

model = xgb.XGBClassifier(
    objective = "binary:logistic",
    n_estimators = 300,
    learning_rate=0.1,
    max_depth = 5,
    random_state = seed,
    eval_metric = "logloss"
)

model.fit(x_train, y_train)

# Evaluate on test set
y_pred_proba = model.predict_proba(x_test)
y_pred = model.predict(x_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.4f}")

model.save_model('backend/models/ufc_xgb.json')
print("model saved")

feature_names = x_train.columns.tolist()
with open('backend/models/feature_names.txt', 'w') as f:
    for feature in feature_names:
        f.write(f"{feature}\n")

print("features saved")

label_mapping = {"0": "Red Fighter (Differential) loses", "1": "Red Fighter (Differential) wins", np.nan: "NC/Draw/Cancelled"}
with open('backend/models/labels.txt', 'w') as f:
    json.dump(label_mapping, f, indent=2)

print("labels saved")

metadata = {
    "model_version" : "1.0",
    "training_date" : "10/02/25",
    "test_accuracy" : float(accuracy),
    "num_features" : len(feature_names),
    "num_training_samples" : len(x_train),
    "hyperparameters" : {
        "n_estimators" : "300",
        "learning_rate" : "0.1",
        "max_depth" : "5"
    }
}

# # Check for overfitting
# if abs(lr_score - test_accuracy) < 0.05:
#     print("✓ Model appears to generalize well (difference < 5%)")
# elif abs(lr_score - test_accuracy) < 0.10:
#     print("⚠ Possible slight overfitting (difference 5-10%)")
# else:
#     print("✗ Likely overfitting (difference > 10%)")