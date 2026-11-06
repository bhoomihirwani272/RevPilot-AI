import pandas as pd
from pathlib import Path

# =====================================
# 1. PATHS AND DATA LOADING
# =====================================

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

reps = pd.read_csv(DATA / "reps.csv")
territories = pd.read_csv(DATA / "territories.csv")
accounts = pd.read_csv(DATA / "accounts.csv")
opportunities = pd.read_csv(DATA / "opportunities.csv")
quota = pd.read_csv(DATA / "quota_history.csv")

print("\n========== DAY 2: SALES ANALYTICS ==========")


# =====================================
# 2. REPRESENTATIVE SCORECARDS
# =====================================

closed = opportunities[
    opportunities["is_closed"] == 1
]

won = opportunities[
    opportunities["stage"] == "Won"
]

rep_scorecard = reps[
    ["rep_id", "rep_name", "territory_id", "performance_group"]
].copy()

rep_scorecard["total_deals"] = (
    opportunities.groupby("rep_id")["opportunity_id"].count()
    .reindex(rep_scorecard["rep_id"]).fillna(0).values
)

rep_scorecard["won_deals"] = (
    won.groupby("rep_id")["opportunity_id"].count()
    .reindex(rep_scorecard["rep_id"]).fillna(0).values
)

rep_scorecard["closed_deals"] = (
    closed.groupby("rep_id")["opportunity_id"].count()
    .reindex(rep_scorecard["rep_id"]).fillna(0).values
)

rep_scorecard["win_rate"] = (
    rep_scorecard["won_deals"] /
    rep_scorecard["closed_deals"].replace(0, pd.NA)
) * 100

rep_scorecard["win_rate"] = rep_scorecard["win_rate"].fillna(0)

rep_scorecard["won_revenue"] = (
    won.groupby("rep_id")["amount"].sum()
    .reindex(rep_scorecard["rep_id"]).fillna(0).values
)

rep_scorecard.to_csv(
    OUTPUT / "rep_scorecard.csv", index=False
)

print("\n1. REP SCORECARDS")
print(rep_scorecard.head(10).to_string(index=False))


# =====================================
# 3. TERRITORY ANALYTICS
# =====================================

territory_accounts = accounts.groupby(
    "territory_id"
).agg(
    total_accounts=("account_id", "count"),
    active_accounts=("account_status",
                     lambda x: (x == "Active").sum()),
    account_revenue=("annual_revenue", "sum")
).reset_index()

territory_sales = (
    won.merge(
        reps[["rep_id", "territory_id"]],
        on="rep_id"
    )
    .groupby("territory_id")
    .agg(
        won_deals=("opportunity_id", "count"),
        won_revenue=("amount", "sum")
    )
    .reset_index()
)

territory_report = territories.merge(
    territory_accounts, on="territory_id", how="left"
).merge(
    territory_sales, on="territory_id", how="left"
)

territory_report[
    ["won_deals", "won_revenue"]
] = territory_report[
    ["won_deals", "won_revenue"]
].fillna(0)

# Top 5 account concentration
account_totals = accounts.groupby(
    "territory_id"
)["annual_revenue"].apply(
    lambda x: x.nlargest(5).sum()
)

territory_report["top5_concentration"] = (
    territory_report["territory_id"].map(account_totals)
    / territory_report["account_revenue"].replace(0, pd.NA)
) * 100

territory_report["top5_concentration"] = (
    territory_report["top5_concentration"].fillna(0)
)

territory_report["concentration_flag"] = (
    territory_report["top5_concentration"] > 60
)

territory_report.to_csv(
    OUTPUT / "territory_report.csv", index=False
)

print("\n2. TERRITORY PERFORMANCE")
print(territory_report.to_string(index=False))


# =====================================
# 4. QUOTA ATTAINMENT
# =====================================

quota_summary = quota.groupby(
    "rep_id"
).agg(
    total_quota=("quota", "sum"),
    actual_sales=("actual_sales", "sum")
).reset_index()

quota_summary["attainment_percentage"] = (
    quota_summary["actual_sales"] /
    quota_summary["total_quota"]
) * 100


def attainment_status(value):
    if value >= 100:
        return "Exceeding"
    elif value >= 70:
        return "On Track"
    elif value >= 50:
        return "Behind"
    return "At Risk"


quota_summary["status"] = (
    quota_summary["attainment_percentage"]
    .apply(attainment_status)
)

quota_summary = quota_summary.merge(
    reps[["rep_id", "rep_name"]],
    on="rep_id"
)

quota_summary.to_csv(
    OUTPUT / "quota_summary.csv", index=False
)

print("\n3. QUOTA ATTAINMENT")
print(quota_summary.head(10).to_string(index=False))


# =====================================
# 5. PIPELINE ANALYTICS
# =====================================

stage_probability = {
    "Prospecting": 0.10,
    "Qualification": 0.25,
    "Proposal": 0.50,
    "Negotiation": 0.75,
    "Closing": 0.90
}

open_deals = opportunities[
    ~opportunities["stage"].isin(["Won", "Lost"])
].copy()

open_deals["stage_probability"] = (
    open_deals["stage"].map(stage_probability)
)

open_deals["weighted_pipeline"] = (
    open_deals["amount"] *
    open_deals["stage_probability"]
)

open_deals.to_csv(
    OUTPUT / "pipeline_details.csv", index=False
)

pipeline_summary = open_deals.groupby(
    "stage"
).agg(
    deal_count=("opportunity_id", "count"),
    pipeline_value=("amount", "sum"),
    weighted_value=("weighted_pipeline", "sum")
).reset_index()

pipeline_summary.to_csv(
    OUTPUT / "pipeline_summary.csv", index=False
)

print("\n4. PIPELINE ANALYTICS")
print(pipeline_summary.to_string(index=False))

print(
    "\nTotal Open Pipeline:",
    f"₹{open_deals['amount'].sum():,.2f}"
)

print(
    "Weighted Pipeline:",
    f"₹{open_deals['weighted_pipeline'].sum():,.2f}"
)


# =====================================
# 6. COMPLETION
# =====================================

print("\n=====================================")
print("DAY 2 ANALYTICS COMPLETED")
print("=====================================")

print("\nGenerated files:")

for file in OUTPUT.glob("*.csv"):
    print(file.name)