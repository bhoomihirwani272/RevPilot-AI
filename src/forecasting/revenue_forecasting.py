import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
import os

# Load sales data
df = pd.read_csv("data/processed/opportunities_ml_ready.csv")

# Keep only successful deals
df = df[df["won"] == 1].copy()

# Convert date
df["created_date"] = pd.to_datetime(df["created_date"])

# Prepare monthly revenue
monthly = df.groupby(
    df["created_date"].dt.to_period("M")
)["amount"].sum().reset_index()

monthly.columns = ["ds", "y"]
monthly["ds"] = monthly["ds"].dt.to_timestamp()

print("\n========== MONTHLY REVENUE ==========")
print(monthly)

# Create output folder
os.makedirs("output", exist_ok=True)

if len(monthly) >= 2:

    # Create forecasting model
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    # Train model
    model.fit(monthly)

    # Predict next six months
    future = model.make_future_dataframe(periods=6, freq="MS")
    forecast = model.predict(future)

    # Save forecast
    forecast.to_csv(
        "output/forecast_results.csv",
        index=False
    )

    # Plot forecast
    fig = model.plot(forecast)

    plt.title("Sales Revenue Forecast")
    plt.xlabel("Date")
    plt.ylabel("Revenue")

    plt.savefig("output/revenue_forecast.png")
    plt.close()

    print("\nNext 6 Months Forecast:")

    print(
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        .tail(6)
    )

    print("\nForecast completed successfully!")

else:
    print("Not enough monthly data for forecasting.")
