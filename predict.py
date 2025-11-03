#scraping

#import libraries
import pandas as pd
import numpy as np
import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

raw = pd.read_csv('/Users/shahinsheikh/ufc-predictor-web/data/UFC_Final.csv')

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
    return df

raw = map_winner_to_color(raw)

raw.drop(columns=['RedFighter', 'BlueFighter', 'Date', 'Location', 'Event', 'Victory_Method', 'Victory_Result', 'WL','Title','Fight_Bonus','Perf_Bonus','Sub_Bonus','KO_Bonus'], inplace = True)

stance_map = {'Orthodox':0, 'Southpaw':1, 'Switch':2, 'Open Stance':3}
raw['Blue_stance'] = raw['Blue_stance'].replace(stance_map)
raw['Red_stance'] = raw['Red_stance'].replace(stance_map)

win_map = {'Red': 0, 'Blue':1, np.nan:2}
raw['Winner'] = raw['Winner'].replace(win_map)
raw['Winner'].replace(np.nan, 2, inplace = True)

x = raw.drop(columns=['Winner'])
y = raw['Winner']

#fill nan values with average per weight class
def fill_nan(x):
    df_filled = x.copy()
    num_cols = df_filled.select_dtypes(include = [np.number]).columns
    df_filled[num_cols] = df_filled.groupby('Weight_Class')[num_cols].transform(lambda x: x.fillna(x.mean()))

    remaining_na = df_filled[num_cols].isna().sum().sum()
    if remaining_na > 0:
        df_filled[num_cols] = df_filled[num_cols].fillna((df_filled[num_cols].mean()))

    return df_filled

x = fill_nan(x)

x.replace(np.nan, 0, inplace = True)

x = x.select_dtypes(include=[np.number]) 

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state = 42)

seed = 350
np.random.seed(seed)

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.fit_transform(x_test)

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

# # Check for overfitting
# if abs(lr_score - test_accuracy) < 0.05:
#     print("✓ Model appears to generalize well (difference < 5%)")
# elif abs(lr_score - test_accuracy) < 0.10:
#     print("⚠ Possible slight overfitting (difference 5-10%)")
# else:
#     print("✗ Likely overfitting (difference > 10%)")