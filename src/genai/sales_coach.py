
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Load representative performance
df = pd.read_csv("data/processed/rep_scorecard.csv")

print("\n========== AI SALES COACHING ==========")

# Initialize OpenAI only if API key exists
client = OpenAI(api_key=api_key) if api_key else None

for _, row in df.head(5).iterrows():

    rep_id = row["rep_id"]

    performance = f"""
    Representative ID: {rep_id}
    Total Deals: {row['total_deals']}
    Won Deals: {row['won_deals']}
    Win Rate: {row['win_rate']}%
    Won Revenue: {row['won_revenue']}
    """

    prompt = f"""
    You are a professional sales coach.

    Analyze this sales representative's performance:

    {performance}

    Give:
    1. Three strengths.
    2. Three improvement areas.
    3. Three practical actions for the next 30 days.

    Use simple, professional language.
    Do not invent performance data.
    """

    print(f"\nRepresentative: {rep_id}")

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            advice = response.choices[0].message.content

        except Exception as e:
            advice = f"AI request failed: {e}"

    else:
        advice = (
            "Demo mode: OpenAI API key not configured. "
            "Connect an API key to generate personalized coaching."
        )

    print(advice)

    # Save coaching results
    os.makedirs("output", exist_ok=True)

    with open(
        f"output/coaching_{rep_id}.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(advice)

print("\nCoaching generation completed!")
