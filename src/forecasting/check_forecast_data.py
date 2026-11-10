import pandas as pd

# Load opportunities dataset
df = pd.read_csv("data/processed/opportunities_ml_ready.csv")

# Convert date column
df["created_date"] = pd.to_datetime(df["created_date"])

print("\n========== DATASET INFORMATION ==========")

print("Total Records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nDate Range:")
print("Start Date:", df["created_date"].min())
print("End Date:", df["created_date"].max())

# Consider only won deals for revenue calculation
won_deals = df[df["won"] == 1].copy()

print("\n========== WON DEAL INFORMATION ==========")

print("Total Won Deals:", len(won_deals))
print("Total Won Revenue:", won_deals["amount"].sum())

# Monthly revenue
monthly_revenue = (
    won_deals.groupby(
        won_deals["created_date"].dt.to_period("M")
    )["amount"]
    .sum()
)

print("\n========== MONTHLY REVENUE ==========")
print(monthly_revenue)

# Check commission dataset
commission_df = pd.read_csv("data/raw/commissions.csv")

print("\n========== COMMISSION DATA ==========")
print("Columns:", commission_df.columns.tolist())
print(commission_df.head())