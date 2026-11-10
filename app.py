import os
import glob
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# SALESVISION AI - AGENTAI-035
# Native Streamlit dashboard: no HTML/CSS is rendered as text.
# ============================================================

st.set_page_config(
    page_title="SalesVision AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent


# ------------------------- OPTIONAL AI MODULES -------------------------

try:
    from src.genai.sales_agent import answer_question
except Exception:
    answer_question = None

try:
    from src.genai.deal_predictor import predict_open_deals
except Exception:
    predict_open_deals = None


# ------------------------- THEME / LAYOUT -------------------------

# ------------------------- THEME / LAYOUT -------------------------

st.markdown("""
<style>

/* Workspace dropdown background */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
}

/* Selected workspace text */
section[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #172554 !important;
    font-weight: 600 !important;
}

/* Dropdown options */
[data-baseweb="popover"] [role="option"] {
    color: #172554 !important;
    background-color: #ffffff !important;
}

/* Dropdown hover effect */
[data-baseweb="popover"] [role="option"]:hover {
    background-color: #e0e7ff !important;
    color: #172554 !important;
}

</style>
""", unsafe_allow_html=True)


# ------------------------- DATA HELPERS -------------------------

# ------------------------- DATA HELPERS -------------------------

def project_path(relative_path):
    return BASE_DIR / relative_path


@st.cache_data(show_spinner=False)
def load_data(relative_path):
    path = project_path(relative_path)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def find_col(df, *keywords):
    if df is None or df.empty:
        return None
    for keyword in keywords:
        key = str(keyword).lower()
        for column in df.columns:
            if key in str(column).lower():
                return column
    return None


def number_series(df, column):
    if df is None or df.empty or not column:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").dropna()


def total_value(df, *keywords):
    col = find_col(df, *keywords)
    values = number_series(df, col)
    return float(values.sum()) if not values.empty else 0.0


def average_value(df, *keywords):
    col = find_col(df, *keywords)
    values = number_series(df, col)
    return float(values.mean()) if not values.empty else 0.0


def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def percent(value):
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


def show_table(df, height=380):
    if df is None or df.empty:
        st.info("No data is available for this section yet.")
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=height,
        )


def page_header(title, description, tag="SALES INTELLIGENCE"):
    st.caption(tag)
    st.title(title)
    st.write(description)
    st.divider()


def style_chart(fig, height=390):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial", color="#334155", size=12),
        title_font=dict(size=17, color="#172554"),
        height=height,
        margin=dict(l=25, r=25, t=58, b=30),
        hoverlabel=dict(bgcolor="#ffffff", font_color="#172554"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#edf1f7", zeroline=False)
    return fig


def metric_row(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.metric(item[0], item[1], item[2] if len(item) > 2 else None)


def search_rows(df, query):
    if df.empty or not query:
        return df
    mask = df.astype(str).apply(
        lambda column: column.str.contains(query, case=False, na=False)
    ).any(axis=1)
    return df[mask]


# ------------------------- LOAD ALL REPORTS ONCE -------------------------

rep_df = load_data("data/processed/rep_scorecard.csv")
territory_df = load_data("data/processed/territory_report.csv")
quota_df = load_data("data/processed/quota_summary.csv")
pipeline_df = load_data("data/processed/pipeline_summary.csv")
deal_df = load_data("data/processed/deal_health_report.csv")
commission_df = load_data("data/processed/commission_report.csv")
pipeline_details_df = load_data("data/processed/pipeline_details.csv")
forecast_df = load_data("output/forecast_results.csv")

# Shared values are defined globally so every page can use them.
total_opportunities = len(pipeline_details_df)
total_reps = len(rep_df)
open_pipeline_value = total_value(pipeline_details_df, "amount", "opportunity_value")
total_sales = total_value(quota_df, "actual_sales", "won_revenue")
total_quota = total_value(quota_df, "total_quota", "quota")
avg_attainment = average_value(quota_df, "attainment_percentage", "attainment")
avg_win_rate = average_value(rep_df, "win_rate")
total_commission = total_value(commission_df, "commission")


# ------------------------- SIDEBAR / WORKSPACE -------------------------

with st.sidebar:
    st.markdown("# 📊 SalesVision AI")
    st.caption("AI-powered sales management")
    st.divider()

    st.markdown("### Workspace")
    role = st.selectbox(
        "Choose your workspace",
        ["CRO", "Sales Manager", "Sales Representative"],
        index=0,
        key="workspace_role",
    )

    st.divider()
    st.markdown("### Navigation")
    pages = [
        "Overview",
        "Representatives",
        "Territories",
        "Quotas",
        "Pipeline Analysis",
        "Revenue Forecast",
        "Commission",
        "AI Coaching",
        "AI Sales Assistant",
        "Reports",
        "Admin",
    ]
    page = st.radio("Go to", pages, label_visibility="collapsed")

    st.divider()
    st.success("Dashboard is running")
    st.caption("AgentAI-035 · Demo data environment")


# ------------------------- ROLE CONTEXT -------------------------

rep_id_col = find_col(rep_df, "rep_id", "representative")
rep_name_col = find_col(rep_df, "rep_name", "representative_name", "name")
rep_label_col = rep_name_col or rep_id_col

selected_rep = None
rep_view_df = rep_df.copy()

if not rep_df.empty and rep_label_col:
    rep_options = rep_df[rep_label_col].dropna().astype(str).unique().tolist()
    if rep_options:
        if role == "Sales Representative":
            st.sidebar.markdown("### Representative")
            selected_rep = st.sidebar.selectbox(
                "Select representative",
                rep_options,
                key="selected_rep",
            )
            rep_view_df = rep_df[
                rep_df[rep_label_col].astype(str) == selected_rep
            ].copy()


# ============================================================
# OVERVIEW - ROLE-AWARE WORKSPACE
# ============================================================

if page == "Overview":
    if role == "CRO":
        page_header(
            "Executive Command Center",
            "A company-wide view of revenue performance, forecast health, pipeline exposure and sales execution.",
            "CRO WORKSPACE  /  EXECUTIVE VIEW",
        )
        metric_row([
            ("Total sales", money(total_sales)),
            ("Open pipeline", money(open_pipeline_value)),
            ("Quota attainment", percent(avg_attainment)),
            ("Average win rate", percent(avg_win_rate)),
            ("Sales representatives", str(total_reps)),
        ])

        st.write("")
        left, right = st.columns([1.35, 1])
        with left:
            st.subheader("Revenue contribution")
            rep_revenue_col = find_col(rep_df, "won_revenue", "revenue")
            if rep_label_col and rep_revenue_col and not rep_df.empty:
                chart = rep_df.copy()
                chart[rep_revenue_col] = pd.to_numeric(chart[rep_revenue_col], errors="coerce")
                chart = chart.nlargest(10, rep_revenue_col)
                fig = px.bar(
                    chart.sort_values(rep_revenue_col),
                    x=rep_revenue_col,
                    y=rep_label_col,
                    orientation="h",
                    color=rep_revenue_col,
                    color_continuous_scale="Blues",
                    title="Top 10 representatives by won revenue",
                )
                fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Won revenue")
                st.plotly_chart(style_chart(fig, 420), use_container_width=True)
            else:
                st.info("Representative revenue data is not available.")

        with right:
            st.subheader("Territory performance")
            terr_col = find_col(territory_df, "territory_name", "territory_id")
            terr_rev_col = find_col(territory_df, "won_revenue", "revenue")
            if terr_col and terr_rev_col and not territory_df.empty:
                fig = px.bar(
                    territory_df,
                    x=terr_col,
                    y=terr_rev_col,
                    color=terr_rev_col,
                    color_continuous_scale="Teal",
                    title="Won revenue by territory",
                )
                fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Won revenue")
                st.plotly_chart(style_chart(fig, 420), use_container_width=True)
            else:
                st.info("Territory performance data is not available.")

        left, right = st.columns(2)
        with left:
            st.subheader("Pipeline overview")
            show_table(pipeline_df, 300)
        with right:
            st.subheader("Executive priorities")
            risk_col = find_col(deal_df, "risk_level", "risk")
            if risk_col and not deal_df.empty:
                risk_counts = deal_df[risk_col].astype(str).value_counts().reset_index()
                risk_counts.columns = ["Risk level", "Deals"]
                fig = px.pie(
                    risk_counts,
                    names="Risk level",
                    values="Deals",
                    hole=0.62,
                    color="Risk level",
                    color_discrete_map={
                        "High": "#dc5353",
                        "Medium": "#e6a23c",
                        "Low": "#239b78",
                    },
                    title="Deal risk mix",
                )
                st.plotly_chart(style_chart(fig, 300), use_container_width=True)
            else:
                st.info("Deal risk breakdown will appear when risk data is available.")
            st.metric("Commission recorded", money(total_commission))

        st.subheader("Latest representative scorecard")
        show_table(
            rep_df.sort_values(
                rep_revenue_col, ascending=False
            ).head(10) if rep_revenue_col and not rep_df.empty else rep_df.head(10),
            350,
        )

    elif role == "Sales Manager":
        page_header(
            "Team Performance Workspace",
            "Monitor team results, identify coaching opportunities and review pipeline execution.",
            "SALES MANAGER WORKSPACE",
        )
        metric_row([
            ("Team members", str(total_reps)),
            ("Team won revenue", money(total_sales)),
            ("Open pipeline", money(open_pipeline_value)),
            ("Team win rate", percent(avg_win_rate)),
        ])
        st.write("")
        left, right = st.columns(2)
        with left:
            st.subheader("Team leaderboard")
            rev_col = find_col(rep_df, "won_revenue", "revenue")
            if rep_label_col and rev_col and not rep_df.empty:
                chart = rep_df.copy()
                chart[rev_col] = pd.to_numeric(chart[rev_col], errors="coerce")
                chart = chart.nlargest(10, rev_col)
                fig = px.bar(
                    chart.sort_values(rev_col),
                    x=rev_col,
                    y=rep_label_col,
                    orientation="h",
                    color=rev_col,
                    color_continuous_scale="Viridis",
                    title="Top team contributors",
                )
                fig.update_layout(coloraxis_showscale=False, yaxis_title="")
                st.plotly_chart(style_chart(fig, 390), use_container_width=True)
            else:
                st.info("Team leaderboard is not available.")
        with right:
            st.subheader("Quota progress")
            attainment_col = find_col(quota_df, "attainment_percentage", "attainment")
            quota_rep_col = find_col(quota_df, "rep_id", "representative")
            if attainment_col and quota_rep_col and not quota_df.empty:
                fig = px.bar(
                    quota_df,
                    x=quota_rep_col,
                    y=attainment_col,
                    color=attainment_col,
                    color_continuous_scale="RdYlGn",
                    title="Attainment by representative",
                )
                fig.update_layout(coloraxis_showscale=False, xaxis_title="")
                st.plotly_chart(style_chart(fig, 390), use_container_width=True)
            else:
                st.info("Quota attainment data is not available.")
        st.subheader("Team scorecard")
        show_table(rep_df, 390)

    else:
        page_header(
            "My Sales Performance",
            "Review your sales results, quota progress and coaching signals in one place.",
            "SALES REPRESENTATIVE WORKSPACE",
        )
        if rep_view_df.empty:
            st.info("Select a representative from the Workspace panel to view their performance.")
        else:
            own_revenue = total_value(rep_view_df, "won_revenue", "revenue")
            own_win_rate = average_value(rep_view_df, "win_rate")
            own_attainment = average_value(rep_view_df, "attainment_percentage", "attainment")
            metric_row([
                ("Won revenue", money(own_revenue)),
                ("Win rate", percent(own_win_rate)),
                ("Quota attainment", percent(own_attainment)),
            ])
            st.subheader(f"Performance details — {selected_rep}")
            show_table(rep_view_df, 300)
            st.info("Use AI Coaching to review the coaching report generated for your representative profile.")

    st.divider()
    st.caption("All figures are calculated from the latest CSV reports available in the project data folders.")


# ============================================================
# REPRESENTATIVES
# ============================================================

elif page == "Representatives":
    page_header(
        "Representative Performance",
        "Search the scorecard and compare revenue, win rate and quota outcomes.",
    )
    if rep_df.empty:
        st.warning("Representative scorecard not found. Run the analytics pipeline first.")
    else:
        query = st.text_input("Search representative", placeholder="Enter representative ID or name")
        filtered = search_rows(rep_df.copy(), query)
        show_table(filtered, 420)
        label_col = find_col(filtered, "rep_name", "representative_name", "name", "rep_id")
        win_col = find_col(filtered, "win_rate")
        if label_col and win_col and not filtered.empty:
            fig = px.bar(
                filtered,
                x=label_col,
                y=win_col,
                color=win_col,
                color_continuous_scale="Viridis",
                title="Win rate by representative",
            )
            fig.update_layout(coloraxis_showscale=False, xaxis_title="")
            st.plotly_chart(style_chart(fig, 410), use_container_width=True)


# ============================================================
# TERRITORIES
# ============================================================

elif page == "Territories":
    page_header(
        "Territory Intelligence",
        "Compare regional outcomes and understand where sales performance is strongest.",
    )
    if territory_df.empty:
        st.warning("Territory report not found.")
    else:
        show_table(territory_df, 350)
        territory_col = find_col(territory_df, "territory_name", "territory_id")
        numeric_cols = territory_df.select_dtypes(include="number").columns.tolist()
        if territory_col and numeric_cols:
            preferred = find_col(territory_df, "won_revenue", "revenue")
            default_index = numeric_cols.index(preferred) if preferred in numeric_cols else 0
            metric = st.selectbox("Compare using", numeric_cols, index=default_index)
            fig = px.bar(
                territory_df,
                x=territory_col,
                y=metric,
                color=metric,
                color_continuous_scale="Tealgrn",
                title=f"Territory comparison — {metric}",
            )
            fig.update_layout(coloraxis_showscale=False, xaxis_title="")
            st.plotly_chart(style_chart(fig, 430), use_container_width=True)


# ============================================================
# QUOTAS
# ============================================================

elif page == "Quotas":
    page_header(
        "Quota Management",
        "Track actual sales against assigned targets and identify attainment gaps.",
    )
    if quota_df.empty:
        st.warning("Quota summary not found.")
    else:
        metric_row([
            ("Actual sales", money(total_value(quota_df, "actual_sales"))),
            ("Assigned quota", money(total_value(quota_df, "total_quota"))),
            ("Average attainment", percent(average_value(quota_df, "attainment_percentage"))),
        ])
        st.write("")
        show_table(quota_df, 420)
        rep_col = find_col(quota_df, "rep_id", "representative")
        attainment_col = find_col(quota_df, "attainment_percentage", "attainment")
        if rep_col and attainment_col:
            fig = px.bar(
                quota_df,
                x=rep_col,
                y=attainment_col,
                color=attainment_col,
                color_continuous_scale="RdYlGn",
                title="Quota attainment by representative",
            )
            fig.update_layout(coloraxis_showscale=False, xaxis_title="")
            st.plotly_chart(style_chart(fig, 420), use_container_width=True)


# ============================================================
# PIPELINE ANALYSIS
# ============================================================

elif page == "Pipeline Analysis":
    page_header(
        "Pipeline & Deal Health",
        "Review opportunity stages, deal quality and the value of active opportunities.",
    )
    metric_row([
        ("Total opportunities", f"{total_opportunities:,}"),
        ("Open pipeline value", money(open_pipeline_value)),
        ("Deals in health report", f"{len(deal_df):,}"),
    ])
    left, right = st.columns(2)
    with left:
        st.subheader("Pipeline summary")
        show_table(pipeline_df, 320)
    with right:
        st.subheader("Deal health")
        if deal_df.empty:
            st.info("Deal health report not found.")
        else:
            score_col = find_col(deal_df, "health_score", "deal_health")
            if score_col:
                fig = px.histogram(
                    deal_df,
                    x=score_col,
                    nbins=14,
                    title="Deal health score distribution",
                    color_discrete_sequence=["#6256c9"],
                )
                st.plotly_chart(style_chart(fig, 300), use_container_width=True)
            show_table(deal_df, 260)

    if not pipeline_details_df.empty:
        st.subheader("Opportunity explorer")
        query = st.text_input("Find an opportunity", placeholder="Opportunity ID, account or rep")
        show_table(search_rows(pipeline_details_df.copy(), query), 440)
    else:
        st.info("Opportunity-level details are not available yet.")


# ============================================================
# REVENUE FORECAST
# ============================================================

elif page == "Revenue Forecast":
    page_header(
        "Revenue Forecast",
        "Explore the revenue projection and confidence range generated by the forecasting workflow.",
    )
    if forecast_df.empty:
        st.warning("Forecast results not found. Run the forecasting script first.")
    else:
        date_col = find_col(forecast_df, "ds", "date")
        forecast_col = find_col(forecast_df, "yhat", "forecast")
        lower_col = find_col(forecast_df, "yhat_lower")
        upper_col = find_col(forecast_df, "yhat_upper")
        if not date_col or not forecast_col:
            st.error("The forecast file needs a date column and a forecast value column.")
        else:
            chart_df = forecast_df.copy()
            chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors="coerce")
            chart_df[forecast_col] = pd.to_numeric(chart_df[forecast_col], errors="coerce")
            chart_df = chart_df.dropna(subset=[date_col, forecast_col]).sort_values(date_col)
            if chart_df.empty:
                st.warning("No valid forecast rows were found.")
            else:
                st.metric("Latest projected value", money(chart_df[forecast_col].iloc[-1]))
                fig = go.Figure()
                if lower_col and upper_col:
                    chart_df[lower_col] = pd.to_numeric(chart_df[lower_col], errors="coerce")
                    chart_df[upper_col] = pd.to_numeric(chart_df[upper_col], errors="coerce")
                    fig.add_trace(go.Scatter(
                        x=chart_df[date_col], y=chart_df[upper_col],
                        mode="lines", line=dict(width=0),
                        showlegend=False, hoverinfo="skip",
                    ))
                    fig.add_trace(go.Scatter(
                        x=chart_df[date_col], y=chart_df[lower_col],
                        mode="lines", fill="tonexty",
                        fillcolor="rgba(98,86,201,.14)",
                        line=dict(width=0), name="Forecast range",
                    ))
                fig.add_trace(go.Scatter(
                    x=chart_df[date_col],
                    y=chart_df[forecast_col],
                    mode="lines+markers",
                    line=dict(color="#5145cd", width=3),
                    marker=dict(size=7),
                    name="Predicted revenue",
                ))
                fig.update_layout(title="Projected revenue over time", hovermode="x unified")
                st.plotly_chart(style_chart(fig, 470), use_container_width=True)
                st.subheader("Forecast values")
                show_table(chart_df.tail(12), 320)
                st.info("Forecasts are model estimates. Review them alongside actual sales and pipeline data.")


# ============================================================
# COMMISSION
# ============================================================

elif page == "Commission":
    page_header(
        "Commission Management",
        "Review calculated payouts and compare commission amounts across representatives.",
    )
    if commission_df.empty:
        st.warning("Commission report not found. Run the commission calculation script first.")
    else:
        commission_col = find_col(commission_df, "commission", "payout")
        rep_col = find_col(commission_df, "rep_id", "representative")
        if commission_col:
            values = number_series(commission_df, commission_col)
            metric_row([
                ("Total commission", money(values.sum())),
                ("Average payout", money(values.mean() if not values.empty else 0)),
                ("Representatives paid", str(commission_df[rep_col].nunique() if rep_col else len(commission_df))),
            ])
            if rep_col:
                fig = px.bar(
                    commission_df,
                    x=rep_col,
                    y=commission_col,
                    color=commission_col,
                    color_continuous_scale="Sunset",
                    title="Commission by representative",
                )
                fig.update_layout(coloraxis_showscale=False, xaxis_title="")
                st.plotly_chart(style_chart(fig, 420), use_container_width=True)
        show_table(commission_df, 420)


# ============================================================
# AI COACHING
# ============================================================

elif page == "AI Coaching":
    page_header(
        "AI Coaching Center",
        "Read the coaching reports generated from representative performance data.",
        "AI-POWERED ENABLEMENT",
    )
    coaching_files = sorted(glob.glob(str(project_path("output/coaching_*.txt"))))
    if not coaching_files:
        st.warning("No coaching reports found. Run src/genai/sales_coach.py first.")
    else:
        rep_files = {
            Path(file).name.replace("coaching_", "").replace(".txt", ""): file
            for file in coaching_files
        }
        selected = st.selectbox("Choose representative", list(rep_files.keys()))
        with open(rep_files[selected], "r", encoding="utf-8") as file:
            coaching_text = file.read()
        st.subheader(f"Coaching report — {selected}")
        st.text_area("Report", coaching_text, height=360)
        st.download_button(
            "Download coaching report",
            data=coaching_text,
            file_name=f"{selected}_coaching.txt",
            mime="text/plain",
        )


# ============================================================
# AI SALES ASSISTANT
# ============================================================

elif page == "AI Sales Assistant":
    page_header(
        "AI Sales Assistant",
        "Ask questions about representatives, territories, pipeline performance and deal risk.",
        "CONVERSATIONAL SALES ANALYTICS",
    )
    st.info(
        "Try: Who is the best representative? Which territory performs best? "
        "What is the pipeline summary?"
    )

    if "sales_chat_history" not in st.session_state:
        st.session_state.sales_chat_history = []

    if st.button("Clear conversation"):
        st.session_state.sales_chat_history = []
        st.rerun()

    for message in st.session_state.sales_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your sales data...")
    if question:
        st.session_state.sales_chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Reviewing sales data..."):
                try:
                    if answer_question is None:
                        response = (
                            "The sales assistant module could not be loaded. "
                            "Check src/genai/sales_agent.py and its imports."
                        )
                    else:
                        response = answer_question(question)
                    if response is None:
                        response = "I could not find an answer in the available sales reports."
                    response = str(response)
                    st.markdown(response)
                except Exception as error:
                    response = f"Unable to process the question: {error}"
                    st.error(response)

        st.session_state.sales_chat_history.append(
            {"role": "assistant", "content": response}
        )

    if predict_open_deals is not None:
        with st.expander("Open deal risk snapshot"):
            if st.button("Load deal risk predictions"):
                try:
                    risk_df = predict_open_deals()
                    if risk_df is not None and not risk_df.empty:
                        risk_col = find_col(risk_df, "risk_level", "risk")
                        if risk_col:
                            high_risk = risk_df[
                                risk_df[risk_col].astype(str).str.contains("high", case=False, na=False)
                            ]
                            st.subheader("High-risk opportunities")
                            show_table(high_risk, 320)
                        else:
                            show_table(risk_df.head(15), 320)
                    else:
                        st.info("No deal predictions were returned.")
                except Exception as error:
                    st.error(f"Could not load predictions: {error}")


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":
    page_header(
        "Reports & Downloads",
        "Download the generated CSV reports for analysis, review and submission.",
    )
    report_files = [
        ("Representative scorecard", "data/processed/rep_scorecard.csv"),
        ("Territory report", "data/processed/territory_report.csv"),
        ("Quota summary", "data/processed/quota_summary.csv"),
        ("Pipeline summary", "data/processed/pipeline_summary.csv"),
        ("Deal health report", "data/processed/deal_health_report.csv"),
        ("Commission report", "data/processed/commission_report.csv"),
        ("Pipeline details", "data/processed/pipeline_details.csv"),
        ("Revenue forecast", "output/forecast_results.csv"),
    ]
    for label, relative_path in report_files:
        path = project_path(relative_path)
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**{label}**")
                st.caption(relative_path if path.exists() else "Report has not been generated yet.")
            with right:
                if path.exists():
                    st.download_button(
                        "Download",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime="text/csv",
                        key=f"download_{path.name}",
                        use_container_width=True,
                    )
                else:
                    st.caption("Not ready")


# ============================================================
# ADMIN / SYSTEM STATUS
# ============================================================

elif page == "Admin":
    page_header(
        "System Status",
        "Check the availability of the reports, model files and application components.",
        "ADMIN WORKSPACE",
    )
    paths = [
        "data/processed/rep_scorecard.csv",
        "data/processed/territory_report.csv",
        "data/processed/quota_summary.csv",
        "data/processed/pipeline_summary.csv",
        "data/processed/deal_health_report.csv",
        "data/processed/commission_report.csv",
        "data/processed/pipeline_details.csv",
        "output/forecast_results.csv",
        "models/xgb_win_model.joblib",
        "models/model_features.json",
    ]
    rows = []
    for relative_path in paths:
        path = project_path(relative_path)
        rows.append({
            "Component": relative_path,
            "Status": "Available" if path.exists() else "Not found",
            "Size (KB)": round(path.stat().st_size / 1024, 2) if path.exists() else 0,
        })
    status_df = pd.DataFrame(rows)
    ready = int((status_df["Status"] == "Available").sum())
    metric_row([
        ("Available components", f"{ready}/{len(status_df)}"),
        ("Selected workspace", role),
        ("Opportunities loaded", f"{total_opportunities:,}"),
    ])
    show_table(status_df, 420)
    st.divider()
    st.subheader("Application information")
    st.write("**Application:** SalesVision AI")
    st.write("**Internship ID:** AgentAI-035")
    st.write("**Dashboard:** Streamlit")
    st.write("**Deal model:** XGBoost win-probability classifier (when model files are available)")
    st.write("**Forecasting:** Prophet output (when forecast file is available)")
    st.warning(
        "The workspace selector changes the dashboard view for demonstration. "
        "It is not production authentication or a security permission system."
    )


# ------------------------- FOOTER -------------------------

st.divider()
st.caption("SalesVision AI  ·  AgentAI-035  ·  AI-Powered Sales Management System")
