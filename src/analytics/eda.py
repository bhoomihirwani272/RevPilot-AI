import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data" / "raw"
OUTPUT_PATH = ROOT / "output"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

print("\n========== SALES DATA ANALYSIS ==========\n")


# ==========================================
# 2. LOAD DATASETS
# ==========================================

reps = pd.read_csv(DATA_PATH / "reps.csv")
territories = pd.read_csv(DATA_PATH / "territories.csv")
opportunities = pd.read_csv(DATA_PATH / "opportunities.csv")
quota = pd.read_csv(DATA_PATH / "quota_history.csv")

print("All datasets loaded successfully!")


# ==========================================
# 3. SALES PERFORMANCE BY REPRESENTATIVE
# ==========================================

closed_deals = opportunities[
    opportunities["is_closed"] == 1
]

won_deals = opportunities[
    opportunities["stage"] == "Won"
]

rep_sales = won_deals.groupby("rep_id")["amount"].sum()

rep_win_rate = (
    closed_deals.groupby("rep_id")["won"].mean() * 100
)

rep_analysis = reps[
    ["rep_id", "rep_name", "performance_group"]
].copy()

rep_analysis["total_sales"] = (
    rep_analysis["rep_id"]
    .map(rep_sales)
    .fillna(0)
)

rep_analysis["win_rate"] = (
    rep_analysis["rep_id"]
    .map(rep_win_rate)
    .fillna(0)
)

rep_analysis = rep_analysis.sort_values(
    by="total_sales",
    ascending=False
)

print("\n========== TOP 10 SALES REPRESENTATIVES ==========\n")

print(
    rep_analysis[
        ["rep_name", "performance_group", "total_sales", "win_rate"]
    ].head(10).to_string(index=False)
)


# ==========================================
# 4. CHART 1: TOP 10 SALES REPRESENTATIVES
# ==========================================

top_reps = rep_analysis.head(10)

plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_reps,
    x="rep_name",
    y="total_sales"
)

plt.title("Top 10 Sales Representatives by Won Deal Value")
plt.xlabel("Sales Representative")
plt.ylabel("Won Deal Value")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH / "top_sales_representatives.png"
)
plt.close()



# ==========================================
# 5. CHART 2: OPPORTUNITY STAGE DISTRIBUTION
# ==========================================

plt.figure(figsize=(10, 6))

sns.countplot(
    data=opportunities,
    x="stage",
    order=opportunities["stage"].value_counts().index
)

plt.title("Distribution of Sales Opportunities")
plt.xlabel("Sales Stage")
plt.ylabel("Number of Opportunities")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH / "opportunity_stage_distribution.png"
)
plt.close()



# ==========================================
# 6. CHART 3: TERRITORY PERFORMANCE
# ==========================================

territory_sales = (
    won_deals
    .merge(
        reps[["rep_id", "territory_id"]],
        on="rep_id"
    )
    .groupby("territory_id")["amount"]
    .sum()
    .reset_index()
)

territory_analysis = territories.merge(
    territory_sales,
    on="territory_id",
    how="left"
)

territory_analysis["amount"] = (
    territory_analysis["amount"].fillna(0)
)

territory_analysis = territory_analysis.sort_values(
    by="amount",
    ascending=False
)

print("\n========== TERRITORY PERFORMANCE ==========\n")

print(
    territory_analysis[
        ["territory_name", "amount"]
    ].to_string(index=False)
)

plt.figure(figsize=(12, 6))

sns.barplot(
    data=territory_analysis,
    x="territory_name",
    y="amount"
)

plt.title("Sales Performance by Territory")
plt.xlabel("Territory")
plt.ylabel("Won Deal Value")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH / "territory_performance.png"
)
plt.close()


# ==========================================
# 7. CHART 4: PERFORMANCE GROUP COMPARISON
# ==========================================

group_analysis = (
    rep_analysis
    .groupby("performance_group")["total_sales"]
    .mean()
    .reset_index()
)

print("\n========== PERFORMANCE GROUP ANALYSIS ==========\n")

print(group_analysis.to_string(index=False))

plt.figure(figsize=(8, 5))

sns.barplot(
    data=group_analysis,
    x="performance_group",
    y="total_sales",
    order=["High", "Average", "Low"]
)

plt.title("Average Won Deal Value by Performance Group")
plt.xlabel("Performance Group")
plt.ylabel("Average Won Deal Value")

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH / "performance_group_comparison.png"
)
plt.close()


# ==========================================
# 8. QUOTA ATTAINMENT ANALYSIS
# ==========================================

quota["attainment_percentage"] = (
    quota["actual_sales"] / quota["quota"]
) * 100

quota_analysis = (
    quota.groupby("rep_id")
    .agg({
        "actual_sales": "sum",
        "quota": "sum"
    })
    .reset_index()
)

quota_analysis["attainment_percentage"] = (
    quota_analysis["actual_sales"] /
    quota_analysis["quota"]
) * 100

quota_analysis = quota_analysis.merge(
    reps[["rep_id", "rep_name", "performance_group"]],
    on="rep_id"
)

print("\n========== TOP 10 QUOTA PERFORMERS ==========\n")

print(
    quota_analysis.sort_values(
        by="attainment_percentage",
        ascending=False
    )[
        ["rep_name", "performance_group", "attainment_percentage"]
    ].head(10).to_string(index=False)
)


# ==========================================
# 9. FINAL BUSINESS SUMMARY
# ==========================================

total_opportunities = len(opportunities)

total_won = len(won_deals)

total_lost = len(
    opportunities[opportunities["stage"] == "Lost"]
)

overall_win_rate = (
    total_won / (total_won + total_lost)
) * 100

total_won_value = won_deals["amount"].sum()

print("\n========== BUSINESS SUMMARY ==========\n")

print("Total Opportunities:", total_opportunities)
print("Won Deals:", total_won)
print("Lost Deals:", total_lost)

print(f"Overall Win Rate: {overall_win_rate:.2f}%")

print(f"Total Won Deal Value: ₹{total_won_value:,.2f}")

print("\nCharts saved inside:", OUTPUT_PATH)

print("\nEDA COMPLETED SUCCESSFULLY!")