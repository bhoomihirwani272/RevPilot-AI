import pandas as pd

df = pd.read_csv("data/processed/opportunities_ml_ready.csv")

closed = df[df["is_closed"] == 1]

print("Closed deals:", len(closed))

print("\nWin/Loss distribution:")
print(closed["won"].value_counts())

print("\nWin rate:")
print(closed["won"].mean() * 100)

print("\nPrediction probability:")
print(closed["synthetic_win_probability"].describe())
import pandas as pd

df = pd.read_csv("data/processed/opportunities_ml_ready.csv")

closed = df[df["is_closed"] == 1]

print("Total closed deals:", len(closed))
print("\nWon and Lost:")
print(closed["won"].value_counts())

print("\nActual win rate:", round(closed["won"].mean() * 100, 2), "%")