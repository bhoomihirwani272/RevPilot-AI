
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# Load datasets
quota_df = pd.read_csv("data/processed/quota_summary.csv")
reps_df = pd.read_csv("data/raw/reps.csv")

# Display available columns
print("Quota columns:", quota_df.columns.tolist())

# Merge representative information
df = quota_df.merge(reps_df, on="rep_id", how="left")

# Automatically identify columns
attainment_col = next(
    col for col in df.columns
    if "attainment" in col.lower()
)

sales_col = next(
    col for col in df.columns
    if "actual_sales" in col.lower()
)

def calculate_commission(attainment, sales):

    attainment = Decimal(str(attainment))
    sales = Decimal(str(sales))

    if attainment < 50:
        rate = Decimal("0.00")
    elif attainment < 80:
        rate = Decimal("0.02")
    elif attainment <= 100:
        rate = Decimal("0.04")
    else:
        rate = Decimal("0.06")

    accelerator = Decimal("2") if attainment > 100 else Decimal("1")

    commission = sales * rate * accelerator

    return commission.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

# Calculate commission
df["commission"] = df.apply(
    lambda row: calculate_commission(
        row[attainment_col],
        row[sales_col]
    ),
    axis=1
)

# Save output
df.to_csv("data/processed/commission_report.csv", index=False)

print("\n========== COMMISSION REPORT ==========")
print(df[["rep_id", attainment_col, sales_col, "commission"]].head(10))

print("\nTotal Commission:", df["commission"].sum())
print("\nCommission report generated successfully!")
