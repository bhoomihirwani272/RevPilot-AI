import os
import json
import joblib
import pandas as pd

from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)

# 1. Load dataset
df = pd.read_csv("data/processed/opportunities_ml_ready.csv")

df = df[df["is_closed"] == 1].copy()
df["created_date"] = pd.to_datetime(df["created_date"])

df = df.sort_values("created_date").reset_index(drop=True)

# 2. Select features
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

X = df[features]
y = df["won"].astype(int)

# 3. Encode categorical columns
X = pd.get_dummies(X, drop_first=True, dtype=int)

# 4. Chronological 70/15/15 split
n = len(df)

train_end = int(n * 0.70)
val_end = int(n * 0.85)

X_train = X.iloc[:train_end]
X_val = X.iloc[train_end:val_end]
X_test = X.iloc[val_end:]

y_train = y.iloc[:train_end]
y_val = y.iloc[train_end:val_end]
y_test = y.iloc[val_end:]

print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))

# 5. Handle class imbalance
negative = (y_train == 0).sum()
positive = (y_train == 1).sum()

scale_weight = negative / max(positive, 1)

# 6. Create XGBoost model
model = XGBClassifier(
    n_estimators=150,
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_weight,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42
)

# 7. Train
print("\nTraining XGBoost model...")

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# 8. Evaluate on unseen test data
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("\n========== MODEL EVALUATION ==========")

print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print("Precision:", round(precision_score(y_test, predictions, zero_division=0), 4))
print("Recall:", round(recall_score(y_test, predictions, zero_division=0), 4))
print("F1 Score:", round(f1_score(y_test, predictions, zero_division=0), 4))

if y_test.nunique() == 2:
    print("ROC-AUC:", round(roc_auc_score(y_test, probabilities), 4))
    print("PR-AUC:", round(average_precision_score(y_test, probabilities), 4))
else:
    print("ROC-AUC / PR-AUC unavailable: test set contains only one class.")

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# 9. Save model and feature information
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/xgb_win_model.joblib")

with open("models/model_features.json", "w") as f:
    json.dump(list(X.columns), f, indent=4)

print("\nModel saved successfully!")
print("Location: models/xgb_win_model.joblib")
print("Features saved: models/model_features.json")