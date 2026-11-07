import pandas as pd
import xgboost
import sklearn

# Check library versions
print("XGBoost Version:", xgboost.__version__)
print("Scikit-learn Version:", sklearn.__version__)

# Load opportunities
df = pd.read_csv("data/raw/opportunities.csv")

print("\n========== DATASET INFORMATION ==========")

print("Total Records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nStage Distribution:")
print(df["stage"].value_counts())

print("\nWin/Loss Distribution:")
print(df["won"].value_counts(dropna=False))

print("\nDataset Preview:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())

import pandas as pd

df = pd.read_csv("data/raw/opportunities.csv")

print("Columns:")
print(df.columns.tolist())

print("\nStage Distribution:")
print(df["stage"].value_counts())

print("\nWin/Loss Distribution:")
print(df["won"].value_counts(dropna=False))