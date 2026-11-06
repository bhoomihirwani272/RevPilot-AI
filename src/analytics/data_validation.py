import pandas as pd
from pathlib import Path

# ==========================================
# 1. LOAD DATASETS
# ==========================================

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw"

print("\n========== DATA VALIDATION ==========\n")

files = {
    "territories": "territories.csv",
    "reps": "reps.csv",
    "products": "products.csv",
    "accounts": "accounts.csv",
    "opportunities": "opportunities.csv",
    "activities": "activities.csv",
    "quota_history": "quota_history.csv",
    "commissions": "commissions.csv"
}

data = {}

for name, filename in files.items():
    data[name] = pd.read_csv(DATA_PATH / filename)
    print(f"Loaded {filename}: {len(data[name])} records")


# ==========================================
# 2. CHECK MISSING VALUES
# ==========================================

print("\n========== MISSING VALUE CHECK ==========\n")

for name, df in data.items():

    missing = df.isnull().sum().sum()

    if missing == 0:
        print(f"{name}: No missing values")
    else:
        print(f"{name}: {missing} missing values")

        print(df.isnull().sum()[df.isnull().sum() > 0])


# ==========================================
# 3. CHECK DUPLICATE RECORDS
# ==========================================

print("\n========== DUPLICATE CHECK ==========\n")

for name, df in data.items():

    duplicates = df.duplicated().sum()

    print(f"{name}: {duplicates} duplicate rows")


# ==========================================
# 4. CHECK UNIQUE IDs
# ==========================================

print("\n========== UNIQUE ID CHECK ==========\n")

primary_keys = {
    "territories": "territory_id",
    "reps": "rep_id",
    "products": "product_id",
    "accounts": "account_id",
    "opportunities": "opportunity_id",
    "activities": "activity_id"
}

for name, column in primary_keys.items():

    df = data[name]
    unique_count = df[column].nunique()

    if unique_count == len(df):
        print(f"{name}: All {column} values are unique")
    else:
        print(f"WARNING: Duplicate {column} values found!")


# ==========================================
# 5. CHECK RELATIONSHIPS
# ==========================================

print("\n========== RELATIONSHIP CHECK ==========\n")

territory_ids = set(data["territories"]["territory_id"])
rep_ids = set(data["reps"]["rep_id"])
account_ids = set(data["accounts"]["account_id"])
product_ids = set(data["products"]["product_id"])
opportunity_ids = set(data["opportunities"]["opportunity_id"])

# Reps must belong to valid territories
invalid_rep_territories = (
    ~data["reps"]["territory_id"].isin(territory_ids)
).sum()

print("Invalid rep territories:", invalid_rep_territories)

# Accounts must belong to valid reps and territories
invalid_account_reps = (
    ~data["accounts"]["rep_id"].isin(rep_ids)
).sum()

invalid_account_territories = (
    ~data["accounts"]["territory_id"].isin(territory_ids)
).sum()

print("Invalid account representatives:", invalid_account_reps)
print("Invalid account territories:", invalid_account_territories)

# Check whether account and rep territories match
account_rep_check = data["accounts"].merge(
    data["reps"][["rep_id", "territory_id"]],
    on="rep_id",
    suffixes=("_account", "_rep")
)

mismatched_territories = (
    account_rep_check["territory_id_account"]
    != account_rep_check["territory_id_rep"]
).sum()

print("Account-rep territory mismatches:", mismatched_territories)

# Opportunities must reference valid accounts, reps and products
print(
    "Invalid opportunity accounts:",
    (~data["opportunities"]["account_id"].isin(account_ids)).sum()
)

print(
    "Invalid opportunity reps:",
    (~data["opportunities"]["rep_id"].isin(rep_ids)).sum()
)

print(
    "Invalid opportunity products:",
    (~data["opportunities"]["product_id"].isin(product_ids)).sum()
)

# Opportunity rep must match the account's assigned rep
opportunity_account_check = data["opportunities"].merge(
    data["accounts"][["account_id", "rep_id"]],
    on="account_id",
    suffixes=("_opportunity", "_account")
)

rep_mismatches = (
    opportunity_account_check["rep_id_opportunity"]
    != opportunity_account_check["rep_id_account"]
).sum()

print("Opportunity-account rep mismatches:", rep_mismatches)

# Activities must reference valid opportunities
print(
    "Invalid activity opportunities:",
    (~data["activities"]["opportunity_id"].isin(opportunity_ids)).sum()
)

# Activities must reference valid reps and accounts
print(
    "Invalid activity reps:",
    (~data["activities"]["rep_id"].isin(rep_ids)).sum()
)

print(
    "Invalid activity accounts:",
    (~data["activities"]["account_id"].isin(account_ids)).sum()
)


# ==========================================
# 6. CHECK OPPORTUNITY OUTCOMES
# ==========================================

print("\n========== OPPORTUNITY CHECK ==========\n")

opportunities = data["opportunities"]

invalid_won = (
    (opportunities["stage"] == "Won")
    & (opportunities["won"] != 1)
).sum()

invalid_lost = (
    (opportunities["stage"] == "Lost")
    & (opportunities["won"] != 0)
).sum()

invalid_open = (
    (~opportunities["stage"].isin(["Won", "Lost"]))
    & opportunities["won"].notna()
).sum()

print("Incorrect Won outcomes:", invalid_won)
print("Incorrect Lost outcomes:", invalid_lost)
print("Incorrect Open deal outcomes:", invalid_open)

print("\nOpportunity stage distribution:")
print(opportunities["stage"].value_counts())

closed_deals = opportunities[opportunities["is_closed"] == 1]

if len(closed_deals) > 0:
    win_rate = closed_deals["won"].mean() * 100
    print(f"\nClosed Deal Win Rate: {win_rate:.2f}%")


# ==========================================
# 7. CHECK QUOTA HISTORY
# ==========================================

print("\n========== QUOTA CHECK ==========\n")

quota = data["quota_history"]

duplicate_quota_records = quota.duplicated(
    subset=["rep_id", "year", "quarter"]
).sum()

print("Duplicate rep-quarter records:", duplicate_quota_records)

print(
    "Invalid quota representatives:",
    (~quota["rep_id"].isin(rep_ids)).sum()
)

print(
    "Non-positive quotas:",
    (quota["quota"] <= 0).sum()
)


# ==========================================
# 8. FINAL SUMMARY
# ==========================================

print("\n========== DATASET SUMMARY ==========\n")

for name, df in data.items():
    print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")

print("\n========== VALIDATION COMPLETED ==========")