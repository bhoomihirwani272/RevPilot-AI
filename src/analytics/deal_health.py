import pandas as pd
from pathlib import Path

# =====================================
# 1. LOAD DATA
# =====================================

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

opportunities = pd.read_csv(DATA / "opportunities.csv")
activities = pd.read_csv(DATA / "activities.csv")

print("\n========== DEAL HEALTH ANALYSIS ==========")


# =====================================
# 2. STAGE SCORE (40%)
# =====================================

stage_scores = {
    "Prospecting": 20,
    "Qualification": 40,
    "Proposal": 60,
    "Negotiation": 80,
    "Closing": 100,
    "Won": 100,
    "Lost": 0
}

opportunities["stage_score"] = (
    opportunities["stage"].map(stage_scores)
)


# =====================================
# 3. ACTIVITY SCORE (25%)
# =====================================

activity_counts = activities.groupby(
    "opportunity_id"
).size()

opportunities["activity_count"] = (
    opportunities["opportunity_id"]
    .map(activity_counts)
    .fillna(0)
)

# Maximum 10 activities gives full score
opportunities["activity_score"] = (
    opportunities["activity_count"].clip(upper=10) / 10
) * 100


# =====================================
# 4. STAKEHOLDER SCORE (20%)
# =====================================

contact_score = (
    opportunities["contacts_count"].clip(upper=5) / 5
) * 50

decision_score = (
    opportunities["decision_maker_identified"] * 50
)

opportunities["stakeholder_score"] = (
    contact_score + decision_score
)


# =====================================
# 5. VELOCITY SCORE (15%)
# =====================================

# Fewer days in the current stage means a better velocity score.
opportunities["velocity_score"] = (
    100 - opportunities["days_in_stage"].clip(upper=100)
)


# =====================================
# 6. FINAL HEALTH SCORE
# =====================================

opportunities["health_score"] = (
    opportunities["stage_score"] * 0.40
    + opportunities["activity_score"] * 0.25
    + opportunities["stakeholder_score"] * 0.20
    + opportunities["velocity_score"] * 0.15
)

opportunities["health_score"] = (
    opportunities["health_score"].round(2)
)


# =====================================
# 7. HEALTH CATEGORY
# =====================================

def health_category(score):

    if score >= 75:
        return "Strong"

    elif score >= 55:
        return "Healthy"

    elif score >= 35:
        return "At Risk"

    return "Critical"


opportunities["health_status"] = (
    opportunities["health_score"].apply(health_category)
)


# =====================================
# 8. SAVE RESULTS
# =====================================

health_report = opportunities[
    [
        "opportunity_id",
        "rep_id",
        "stage",
        "amount",
        "activity_count",
        "health_score",
        "health_status"
    ]
].copy()

health_report.to_csv(
    OUTPUT / "deal_health_report.csv",
    index=False
)


# =====================================
# 9. DISPLAY SUMMARY
# =====================================

print("\nDeal Health Distribution:")

print(
    health_report["health_status"].value_counts()
)

print("\nTop 10 Healthy Deals:")

print(
    health_report.sort_values(
        "health_score",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\nAverage Deal Health Score:")

print(
    health_report["health_score"].mean().round(2)
)

print("\nDeal health report saved successfully!")

print("\n========== COMPLETED ==========")