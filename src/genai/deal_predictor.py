import os
import json
import joblib
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

MODEL_PATH = os.path.join(BASE_DIR, "models", "xgb_win_model.joblib")
FEATURE_PATH = os.path.join(BASE_DIR, "models", "model_features.json")

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "opportunities_ml_ready.csv"
)


def predict_open_deals():

    # Load trained model
    model = joblib.load(MODEL_PATH)

    # Load training feature names
    with open(FEATURE_PATH, "r") as file:
        feature_names = json.load(file)

    # Load opportunities
    df = pd.read_csv(DATA_PATH)

    # Consider only open deals
    open_deals = df[df["is_closed"] == 0].copy()

    # Select model input features
    feature_columns = [
        "amount",
        "days_in_stage",
        "contacts_count",
        "decision_maker_identified",
        "demo_completed",
        "proposal_sent",
        "competitor_involved",
        "activity_score",
        "lead_source",
        "industry",
        "account_size",
        "stage_at_prediction"
    ]

    X = open_deals[feature_columns].copy()

    # Convert categorical columns into numerical columns
    X = pd.get_dummies(X, drop_first=True, dtype=int)

    # Match the exact training feature structure
    X = X.reindex(
        columns=feature_names,
        fill_value=0
    )

    # Predict win probability
    probabilities = model.predict_proba(X)[:, 1]

    open_deals["win_probability"] = probabilities * 100

    # Assign deal risk
    def risk_level(probability):

        if probability < 40:
            return "High Risk"

        elif probability < 70:
            return "Medium Risk"

        return "Low Risk"

    open_deals["risk_level"] = (
        open_deals["win_probability"].apply(risk_level)
    )

    return open_deals


if __name__ == "__main__":

    deals = predict_open_deals()

    print("\n========== DEAL RISK ANALYSIS ==========")

    print("\nTotal open deals:", len(deals))

    print("\nRisk distribution:")
    print(deals["risk_level"].value_counts())

    print("\nTop 10 high-risk deals:")

    risky_deals = deals.sort_values(
        "win_probability"
    ).head(10)

    print(
        risky_deals[
            [
                "opportunity_id",
                "rep_id",
                "amount",
                "stage",
                "win_probability",
                "risk_level"
            ]
        ].to_string(index=False)
    )