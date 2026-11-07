import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# Load trained model
model = joblib.load("models/xgb_win_model.joblib")

# Prepare same dataset and features
df = pd.read_csv("data/processed/opportunities_ml_ready.csv")
df = df[df["is_closed"] == 1].copy()

features = [
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

X = pd.get_dummies(
    df[features],
    drop_first=True,
    dtype=int
)

# Match training columns
saved_features = model.get_booster().feature_names
X = X.reindex(columns=saved_features, fill_value=0)

# Calculate SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Create output folder
import os
os.makedirs("output", exist_ok=True)

# Global feature importance
shap.summary_plot(
    shap_values,
    X,
    show=False
)

plt.tight_layout()
plt.savefig("output/shap_summary.png", dpi=300)
plt.close()

# Feature importance bar chart
shap.summary_plot(
    shap_values,
    X,
    plot_type="bar",
    show=False
)

plt.tight_layout()
plt.savefig("output/shap_importance.png", dpi=300)
plt.close()

print("SHAP analysis completed!")
print("Saved: output/shap_summary.png")
print("Saved: output/shap_importance.png")