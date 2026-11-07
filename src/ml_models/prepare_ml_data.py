import pandas as pd
import numpy as np
import os

# Reproducibility: same results every time
np.random.seed(42)

# Load datasets
opportunities = pd.read_csv("data/raw/opportunities.csv")
reps = pd.read_csv("data/raw/reps.csv")

print("Preparing data for machine learning...")

# Check representative performance information
print("\nRepresentative columns:")
print(reps.columns.tolist())

# Create a mapping of representative win probabilities
if "win_probability" in reps.columns:
    rep_probabilities = reps.set_index("rep_id")["win_probability"]
else:
    rep_probabilities = pd.Series(dtype=float)

# Create prediction-stage feature
opportunities["stage_at_prediction"] = opportunities["stage"]

# Won/Lost deals must have a stage before the final outcome
previous_stages = ["Proposal", "Negotiation", "Closing"]

closed_mask = opportunities["is_closed"] == 1

opportunities.loc[closed_mask, "stage_at_prediction"] = np.random.choice(
    previous_stages,
    size=closed_mask.sum(),
    p=[0.25, 0.35, 0.40]
)

# Calculate win probability for closed deals
probabilities = []

for _, row in opportunities.iterrows():

    rep_probability = rep_probabilities.get(row["rep_id"], 0.50)

    # Normalize representative probability
    if rep_probability > 1:
        rep_probability = rep_probability / 100

    score = (
        (rep_probability - 0.50) * 1.5
        + (row["decision_maker_identified"] * 0.35)
        + (row["demo_completed"] * 0.25)
        + (row["proposal_sent"] * 0.20)
        + (min(row["contacts_count"], 5) / 5 * 0.20)
        + (min(row["activity_score"], 100) / 100 * 0.15)
        - (row["competitor_involved"] * 0.25)
    )

    probability = 1 / (1 + np.exp(-score))

    probabilities.append(probability)

opportunities["synthetic_win_probability"] = probabilities

# Update outcomes only for closed deals
for index, row in opportunities[closed_mask].iterrows():

    probability = row["synthetic_win_probability"]

    opportunities.loc[index, "won"] = np.random.binomial(
        1, probability
    )

# Keep open deals without a known outcome
opportunities.loc[~closed_mask, "won"] = np.nan

# Ensure output directory exists
os.makedirs("data/processed", exist_ok=True)

# Save separate ML-ready dataset
output_path = "data/processed/opportunities_ml_ready.csv"

opportunities.to_csv(output_path, index=False)

# Summary
closed = opportunities[opportunities["is_closed"] == 1]

print("\n========== ML DATA PREPARATION ==========")

print("Total opportunities:", len(opportunities))
print("Closed deals:", len(closed))
print("Won deals:", int(closed["won"].sum()))
print("Lost deals:", int((closed["won"] == 0).sum()))

print("\nWin/Loss Distribution:")
print(closed["won"].value_counts())

print("\nML-ready dataset saved:", output_path)

print("\nData preparation completed!")