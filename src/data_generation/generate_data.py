
import pandas as pd
import numpy as np
import random
from pathlib import Path

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

random.seed(42)
np.random.seed(42)

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw"
DATA_PATH.mkdir(parents=True, exist_ok=True)

print("\nStarting AgentAI-035 Sales Data Generation...\n")


# ==========================================
# 2. TERRITORIES
# ==========================================

territory_names = [
    "Pune", "Mumbai", "Nagpur", "Delhi", "Bangalore",
    "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Jaipur"
]

territories = []

for i, name in enumerate(territory_names, start=1):
    territories.append({
        "territory_id": f"T{i:02}",
        "territory_name": name,
        "region": (
            "West" if name in
            ["Pune", "Mumbai", "Nagpur", "Ahmedabad"]
            else "Other"
        ),
        "manager_id": f"M{i:02}"
    })

territories_df = pd.DataFrame(territories)


# ==========================================
# 3. SALES REPRESENTATIVES
# ==========================================

first_names = [
    "Rahul", "Priya", "Aman", "Neha", "Rohan",
    "Sneha", "Arjun", "Ananya", "Karan", "Isha"
]

reps = []

for i in range(1, 31):

    territory = territories[(i - 1) % 10]

    # Three performance groups:
    # High performers, average performers, low performers
    if i <= 10:
        performance_group = "High"
        win_probability = 0.75
    elif i <= 20:
        performance_group = "Average"
        win_probability = 0.50
    else:
        performance_group = "Low"
        win_probability = 0.25

    reps.append({
        "rep_id": f"R{i:03}",
        "rep_name": random.choice(first_names) + f"_{i}",
        "territory_id": territory["territory_id"],
        "manager_id": territory["manager_id"],
        "role": "Sales Representative",
        "performance_group": performance_group,
        "win_probability": win_probability,
        "annual_quota": random.randint(3000000, 8000000),
        "joining_date": (
            pd.Timestamp("2023-01-01")
            + pd.Timedelta(days=random.randint(0, 900))
        ),
        "email": f"rep{i}@company.com"
    })

reps_df = pd.DataFrame(reps)


# ==========================================
# 4. PRODUCTS
# ==========================================

categories = [
    "Software", "Hardware", "Cloud Services",
    "Security", "Analytics"
]

products = []

for i in range(1, 31):
    products.append({
        "product_id": f"P{i:03}",
        "product_name": f"Product_{i}",
        "category": random.choice(categories),
        "unit_price": random.randint(10000, 200000)
    })

products_df = pd.DataFrame(products)


# ==========================================
# 5. CUSTOMER ACCOUNTS
# ==========================================

industries = [
    "IT", "Healthcare", "Finance",
    "Manufacturing", "Education", "Retail"
]

accounts = []

for i in range(1, 201):

    rep = random.choice(reps)

    accounts.append({
        "account_id": f"A{i:03}",
        "account_name": f"Company_{i}",
        "territory_id": rep["territory_id"],
        "rep_id": rep["rep_id"],
        "industry": random.choice(industries),
        "company_size": random.choice(
            ["Small", "Medium", "Large"]
        ),
        "annual_revenue": random.randint(500000, 50000000),
        "account_status": random.choices(
            ["Active", "Inactive"],
            weights=[80, 20]
        )[0]
    })

accounts_df = pd.DataFrame(accounts)


# ==========================================
# 6. SALES OPPORTUNITIES
# ==========================================

stages = [
    "Prospecting", "Qualification", "Proposal",
    "Negotiation", "Closing", "Won", "Lost"
]

stage_weights = [15, 15, 15, 15, 10, 15, 15]

opportunities = []

for i in range(1, 601):

    account = random.choice(accounts)
    product = random.choice(products)

    rep = next(
        r for r in reps
        if r["rep_id"] == account["rep_id"]
    )

    stage = random.choices(
        stages,
        weights=stage_weights
    )[0]

    # Generate activity and deal characteristics
    contacts = random.randint(1, 8)
    decision_maker = random.choice([0, 1])
    demo = random.choice([0, 1])
    proposal = random.choice([0, 1])
    competitor = random.choice([0, 1])

    activity_score = random.randint(1, 10)

    # Calculate probability using representative performance
    probability = (
        rep["win_probability"]
        + 0.025 * (activity_score - 5)
        + 0.04 * decision_maker
        + 0.03 * demo
        + 0.02 * proposal
        - 0.04 * competitor
    )

    probability = max(0.05, min(0.95, probability))

    # Closed deals have outcomes; open deals have unknown outcomes
    if stage == "Won":
        won = 1
        is_closed = 1
    elif stage == "Lost":
        won = 0
        is_closed = 1
    else:
        won = np.nan
        is_closed = 0

    created_date = (
        pd.Timestamp("2024-01-01")
        + pd.Timedelta(days=random.randint(0, 850))
    )

    opportunities.append({
        "opportunity_id": f"O{i:04}",
        "account_id": account["account_id"],
        "rep_id": account["rep_id"],
        "product_id": product["product_id"],
        "stage": stage,
        "amount": random.randint(50000, 2000000),
        "created_date": created_date,
        "days_in_stage": random.randint(1, 90),
        "contacts_count": contacts,
        "decision_maker_identified": decision_maker,
        "demo_completed": demo,
        "proposal_sent": proposal,
        "competitor_involved": competitor,
        "activity_score": activity_score,
        "lead_source": random.choice([
            "Website", "Referral", "Advertisement", "Cold Call"
        ]),
        "industry": account["industry"],
        "account_size": account["company_size"],
        "is_closed": is_closed,
        "won": won
    })

opportunities_df = pd.DataFrame(opportunities)


# ==========================================
# 7. SALES ACTIVITIES
# ==========================================

activities = []

activity_types = ["Call", "Email", "Meeting", "Demo"]
activity_outcomes = [
    "Successful", "Follow-up Required", "No Response"
]

for i in range(1, 10001):

    opportunity = random.choice(opportunities)

    activities.append({
        "activity_id": f"ACT{i:05}",
        "opportunity_id": opportunity["opportunity_id"],
        "rep_id": opportunity["rep_id"],
        "account_id": opportunity["account_id"],
        "activity_type": random.choice(activity_types),
        "activity_date": (
            opportunity["created_date"]
            + pd.Timedelta(days=random.randint(0, 180))
        ),
        "duration_minutes": random.randint(5, 120),
        "outcome": random.choices(
            activity_outcomes,
            weights=[50, 30, 20]
        )[0]
    })

activities_df = pd.DataFrame(activities)


# ==========================================
# 8. QUOTA HISTORY
# ==========================================

quota_history = []

for rep in reps:

    for quarter_number in range(1, 9):

        quota = random.randint(700000, 1500000)

        # Different achievement patterns by performance group
        if rep["performance_group"] == "High":
            achievement = random.uniform(1.00, 1.35)
        elif rep["performance_group"] == "Average":
            achievement = random.uniform(0.70, 1.05)
        else:
            achievement = random.uniform(0.35, 0.75)

        quota_history.append({
            "rep_id": rep["rep_id"],
            "year": 2024 + (quarter_number - 1) // 4,
            "quarter": f"Q{(quarter_number - 1) % 4 + 1}",
            "quota": quota,
            "actual_sales": round(quota * achievement, 2)
        })

quota_history_df = pd.DataFrame(quota_history)


# ==========================================
# 9. COMMISSION RULES
# ==========================================

commission_rules = [
    {
        "attainment_min": 0,
        "attainment_max": 50,
        "commission_rate": 0.00
    },
    {
        "attainment_min": 50,
        "attainment_max": 80,
        "commission_rate": 0.02
    },
    {
        "attainment_min": 80,
        "attainment_max": 100,
        "commission_rate": 0.04
    },
    {
        "attainment_min": 100,
        "attainment_max": 999,
        "commission_rate": 0.06
    }
]

commissions_df = pd.DataFrame(commission_rules)


# ==========================================
# 10. SAVE DATASETS
# ==========================================

datasets = {
    "territories.csv": territories_df,
    "reps.csv": reps_df,
    "products.csv": products_df,
    "accounts.csv": accounts_df,
    "opportunities.csv": opportunities_df,
    "activities.csv": activities_df,
    "quota_history.csv": quota_history_df,
    "commissions.csv": commissions_df
}

print("Generating CSV files...\n")

for filename, dataframe in datasets.items():

    file_path = DATA_PATH / filename

    dataframe.to_csv(file_path, index=False)

    print(
        f"Created: {filename} | "
        f"Rows: {len(dataframe)} | "
        f"Columns: {len(dataframe.columns)}"
    )


# ==========================================
# 11. FINAL SUMMARY
# ==========================================

print("\n======================================")
print("DATA GENERATION COMPLETED SUCCESSFULLY")
print("======================================")

print(f"\nFiles saved inside: {DATA_PATH}")

print("\nDataset Summary:")

for filename, dataframe in datasets.items():
    print(f"{filename}: {len(dataframe)} records")

print("\nSales representatives by performance group:")
print(reps_df["performance_group"].value_counts())

print("\nOpportunity stage distribution:")
print(opportunities_df["stage"].value_counts())

print("\nAll datasets generated successfully!")
