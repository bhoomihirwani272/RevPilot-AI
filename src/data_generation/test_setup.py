import pandas as pd
import numpy as np

print("Sales Management System")
print("-----------------------")

data = {
    "Rep_Name": ["Rahul", "Priya", "Aman"],
    "Sales": [120000, 90000, 150000],
    "Target": [100000, 100000, 100000]
}

df = pd.DataFrame(data)
df["Achievement_Percentage"] = (
    df["Sales"] / df["Target"]
) * 100

print(df)