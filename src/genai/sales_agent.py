try:
    from .deal_predictor import predict_open_deals
except ImportError:
    from deal_predictor import predict_open_deals
import os
import pandas as pd


# Project folder
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


# Load project datasets
def load_data(filename):
    path = os.path.join(PROCESSED_DIR, filename)

    if not os.path.exists(path):
        return None

    return pd.read_csv(path)


# Load representative and territory reports
def load_sales_data():

    reps = load_data("rep_scorecard.csv")
    territories = load_data("territory_report.csv")
    opportunities = load_data("opportunities_ml_ready.csv")

    return reps, territories, opportunities


# Generate answers using actual sales data
def answer_question(question):

    reps, territories, opportunities = load_sales_data()

    if reps is None or territories is None or opportunities is None:
        return "Required sales datasets are missing. Please check data/processed/."

    question = question.lower().strip()

    # 1. Best performing representative
        # 1. Best performing representative
    if (
        "best" in question or "top" in question
    ) and any(word in question for word in ["rep", "representative"]):

        best_rep = reps.sort_values(
            "won_revenue", ascending=False
        ).iloc[0]

        return (
            f"Top representative: {best_rep['rep_name']}\n"
            f"Territory: {best_rep['territory_id']}\n"
            f"Won revenue: {best_rep['won_revenue']:,.2f}\n"
            f"Win rate: {best_rep['win_rate']:.2f}%"
        )

    # 2. Representative needing attention
    elif any(word in question for word in [
        "attention", "weakest", "worst", "lowest"
    ]) and any(word in question for word in ["rep", "representative"]):

        lowest_rep = reps.sort_values(
            "win_rate", ascending=True
        ).iloc[0]

        return (
            f"Representative needing attention: {lowest_rep['rep_name']}\n"
            f"Territory: {lowest_rep['territory_id']}\n"
            f"Won revenue: {lowest_rep['won_revenue']:,.2f}\n"
            f"Win rate: {lowest_rep['win_rate']:.2f}%"
        )

    # 3. General representative performance
        # Deal risk analysis using XGBoost
    elif any(word in question for word in [
        "risky", "risk", "likely to be lost",
        "high risk", "deal prediction"
    ]):

        # Get predictions for all open deals
        deals = predict_open_deals()

        # Filter high-risk deals
        risky_deals = deals[
            deals["risk_level"] == "High Risk"
        ].sort_values("win_probability")

        result = (
            "DEAL RISK ANALYSIS\n\n"
            f"Total open deals: {len(deals)}\n"
            f"High-risk deals: {len(risky_deals)}\n\n"
            "Top 5 high-risk opportunities:\n"
        )

        # Display five risky deals
        for _, deal in risky_deals.head(5).iterrows():

            result += (
                f"\nOpportunity: {deal['opportunity_id']}\n"
                f"Representative: {deal['rep_id']}\n"
                f"Amount: {deal['amount']:,.2f}\n"
                f"Win probability: {deal['win_probability']:.2f}%\n"
            )

        return result
    elif "representative" in question or "sales rep" in question:

        return (
            f"Total representatives: {len(reps)}\n"
            f"Average win rate: {reps['win_rate'].mean():.2f}%\n"
            f"Total won revenue: {reps['won_revenue'].sum():,.2f}"
        )

    # 2. Lowest performing representative
    elif any(word in question for word in ["worst rep", "lowest rep", "weakest rep"]):

        lowest_rep = reps.sort_values(
            "won_revenue", ascending=True
        ).iloc[0]

        return (
            f"Representative needing attention: {lowest_rep['rep_name']}\n"
            f"Won revenue: {lowest_rep['won_revenue']:,.2f}\n"
            f"Win rate: {lowest_rep['win_rate']:.2f}%"
        )

    # 3. Overall representative performance
    elif "representative" in question or "sales rep" in question:

        average_win_rate = reps["win_rate"].mean()

        return (
            f"Total representatives: {len(reps)}\n"
            f"Average win rate: {average_win_rate:.2f}%\n"
            f"Total won revenue: {reps['won_revenue'].sum():,.2f}"
        )

    # 4. Territory performance
    elif "territory" in question:

        best_territory = territories.sort_values(
            "won_revenue", ascending=False
        ).iloc[0]

        return (
            f"Best territory: {best_territory['territory_name']}\n"
            f"Region: {best_territory['region']}\n"
            f"Won revenue: {best_territory['won_revenue']:,.2f}\n"
            f"Won deals: {best_territory['won_deals']}"
        )

    # 5. Pipeline information
    elif "pipeline" in question:

        open_deals = opportunities[
            opportunities["is_closed"] == 0
        ]

        closed_deals = opportunities[
            opportunities["is_closed"] == 1
        ]

        pipeline_value = open_deals["amount"].sum()

        return (
            f"Total opportunities: {len(opportunities)}\n"
            f"Open opportunities: {len(open_deals)}\n"
            f"Closed opportunities: {len(closed_deals)}\n"
            f"Open pipeline value: {pipeline_value:,.2f}"
        )

    # 6. Win rate
    elif "win rate" in question:

        closed = opportunities[
            opportunities["is_closed"] == 1
        ]

        wins = closed["won"].sum()

        win_rate = (
            wins / len(closed) * 100
            if len(closed) > 0 else 0
        )

        return f"Overall win rate: {win_rate:.2f}%"

    # 7. Revenue information
    elif "revenue" in question or "sales" in question:

        return (
            f"Total won revenue: "
            f"{reps['won_revenue'].sum():,.2f}"
        )

    # 8. Total opportunities
    elif "deal" in question or "opportunit" in question:

        return (
            f"Total opportunities in dataset: "
            f"{len(opportunities)}"
        )

    else:

        return (
            "I can help you analyse your sales data.\n\n"
            "Try asking:\n"
            "- Who is the best sales representative?\n"
            "- Which representative needs attention?\n"
            "- Which territory performs best?\n"
            "- Show me the pipeline summary.\n"
            "- What is our overall win rate?\n"
            "- What is our total revenue?"
        )


# Test the agent
if __name__ == "__main__":

    print("SALES AI ASSISTANT")
    print("-----------------")

    while True:

        question = input("\nYou: ")

        if question.lower() in ["exit", "quit", "stop"]:
            print("Assistant: Goodbye!")
            break

        response = answer_question(question)

        print("\nAssistant:", response)