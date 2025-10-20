#scraping

#import libraries
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import accuracy_score
from sklearn.model_selection import StratifiedKFold

raw = pd.read_json('fighter_data.ndjson', lines=True)

raw.drop(columns=['RedFighter', 'BlueFighter', 'Date', 'Location', 'Country', 'Gender', 'BetterRank', 'Finish', 'FinishDetails', 'FinishRoundTime'], inplace = True)

stance_map = {'Orthodox':0, 'Southpaw':1, 'Switch':2, 'Open Stance':3}
raw['BlueStance'] = raw['BlueStance'].replace(stance_map)
raw['RedStance'] = raw['RedStance'].replace(stance_map)

win_map = {'Red':0, 'Blue':1}
raw['Winner'] = raw['Winner'].replace(win_map)
raw['Winner'].replace(np.nan, 2, inplace = True)

x = raw.drop(columns=['Winner'])
y = raw['Winner']

#fill nan values with average per weight class
def fill_nan(x):
    df_filled = x.copy()
    num_cols = df_filled.select_dtypes(include = [np.number]).columns
    df_filled[num_cols] = df_filled.groupby('WeightClass')[num_cols].transform(lambda x: x.fillna(x.mean()))

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

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(max_iter=1000)
kfold_lr = StratifiedKFold(n_splits = 10, random_state=seed, shuffle = True)
cv_lr = cross_val_score(lr, x_train, y_train, cv = kfold_lr)
lr_score = cv_lr.mean()
lr.fit(x_train, y_train)

print("Kfold score: ", lr_score)