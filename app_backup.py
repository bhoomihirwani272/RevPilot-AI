
from src.genai.sales_agent import answer_questionimport streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="SalesVision AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F5F6FA;
    color: #1E293B;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main headings */

h1 {
    color: #172554 !important;
    font-weight: 800 !important;
    font-size: 30px !important;
}

h2, h3 {
    color: #25346A !important;
    font-weight: 700 !important;
}

p, label {
    color: #475569;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #25245B 55%, #3730A3 100%);
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #D1D5DB !important;
}

/* Sidebar navigation */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 9px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 9px;
    border-radius: 9px;
    transition: 0.2s;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.12);
}

/* KPI cards */

.kpi-card {
    padding: 22px;
    min-height: 145px;
    border-radius: 17px;
    color: white;
    box-shadow: 0 7px 20px rgba(31,41,55,0.10);
    transition: all 0.3s ease;
    animation: appear 0.7s ease;
}

.kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 25px rgba(31,41,55,0.18);
}

.kpi-icon {
    font-size: 27px;
    margin-bottom: 12px;
}

.kpi-title {
    font-size: 13px;
    font-weight: 600;
    opacity: 0.9;
}

.kpi-value {
    font-size: 27px;
    font-weight: 800;
    margin-top: 7px;
}

.kpi-subtitle {
    font-size: 11px;
    margin-top: 7px;
    opacity: 0.85;
}

/* White content cards */

.content-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #E8EAF2;
    box-shadow: 0 4px 14px rgba(31,41,55,0.04);
    margin-bottom: 15px;
}

/* Charts */

div[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 15px;
    padding: 8px;
    border: 1px solid #E8EAF2;
}

/* Tables */

div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    overflow: hidden;
}

/* Buttons */

.stButton button {
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    padding: 8px 18px;
    transition: 0.3s;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 14px rgba(79,70,229,0.3);
}

/* Animation */

@keyframes appear {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.block-container {
    animation: appear 0.5s ease-in-out;
}

hr {
    border-color: #E2E8F0;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# DATA LOADING
# =====================================================

@st.cache_data
def load_data(path):

    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


rep_df = load_data(
    "data/processed/rep_scorecard.csv"
)

territory_df = load_data(
    "data/processed/territory_report.csv"
)

quota_df = load_data(
    "data/processed/quota_summary.csv"
)

pipeline_df = load_data(
    "data/processed/pipeline_summary.csv"
)

deal_df = load_data(
    "data/processed/deal_health_report.csv"
)

commission_df = load_data(
    "data/processed/commission_report.csv"
)

forecast_df = load_data(
    "output/forecast_results.csv"
)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def find_col(df, keyword):

    for col in df.columns:
        if keyword.lower() in col.lower():
            return col

    return None


def money(value):

    return f"₹{value:,.0f}"


def make_chart(fig, height=380):

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter",
            color="#334155",
            size=12
        ),
        title_font=dict(
            size=17,
            color="#172554"
        ),
        height=height,
        margin=dict(
            l=25,
            r=25,
            t=65,
            b=35
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_color="#172554"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#E2E8F0"
    )

    fig.update_yaxes(
        gridcolor="#EEF0F5",
        zeroline=False
    )

    return fig


def show_kpi(title, value, icon, color, subtitle=""):

    st.markdown(f"""
    <div class="kpi-card"
         style="background:linear-gradient(135deg,{color});">

        <div class="kpi-icon">{icon}</div>

        <div class="kpi-title">{title}</div>

        <div class="kpi-value">{value}</div>

        <div class="kpi-subtitle">{subtitle}</div>

    </div>
    """, unsafe_allow_html=True)


def section_title(title, subtitle=None):

    st.markdown(f"## {title}")

    if subtitle:
        st.caption(subtitle)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("# 🚀 SalesVision AI")

st.sidebar.markdown(
    "### Intelligent Sales Management"
)

st.sidebar.markdown("---")

role = st.sidebar.selectbox(
    "👤 Select User Role",
    [
        "CRO",
        "Sales Manager",
        "Sales Representative"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("### MENU")

page = st.sidebar.radio(
    "Navigation",
    [
        "ðŸ  Overview",
        "ðŸ‘¥ Representatives",
        "ðŸŒ Territories",
        "ðŸ“ˆ Pipeline Analysis",
        "ðŸ”® Revenue Forecast",
        "ðŸ’° Commission",
        "ðŸ¤– AI Coaching",
        "AI Sales Assistant"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "🟢 System Status: Online"
)

st.sidebar.caption(
    "AgentAI-035 | Sales Analytics Platform"
)


# =====================================================
# OVERVIEW DASHBOARD
# =====================================================

if page == "🏠 Overview":

    st.title("Sales Performance Overview")

    st.caption(
        "Monitor revenue, sales performance and business growth."
    )

    # Calculate metrics

    total_sales = 0
    total_quota = 0
    avg_attainment = 0

    if not quota_df.empty:

        sales_col = find_col(
            quota_df, "actual_sales"
        )

        quota_col = find_col(
            quota_df, "total_quota"
        )

        attainment_col = find_col(
            quota_df, "attainment_percentage"
        )

        if sales_col:
            total_sales = quota_df[sales_col].sum()

        if quota_col:
            total_quota = quota_df[quota_col].sum()

        if attainment_col:
            avg_attainment = quota_df[
                attainment_col
            ].mean()

    total_reps = len(rep_df)

    total_commission = 0

    if not commission_df.empty:

        commission_col = find_col(
            commission_df, "commission"
        )

        if commission_col:
            total_commission = commission_df[
                commission_col
            ].sum()

    # KPI CARDS

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        show_kpi(
            "TOTAL SALES",
            money(total_sales),
            "💰",
            "#2563EB,#60A5FA",
            "Total recorded sales"
        )

    with c2:
        show_kpi(
            "TOTAL QUOTA",
            money(total_quota),
            "🎯",
            "#7C3AED,#A78BFA",
            "Assigned sales target"
        )

    with c3:
        show_kpi(
            "AVG. ATTAINMENT",
            f"{avg_attainment:.1f}%",
            "📈",
            "#059669,#34D399",
            "Average quota achievement"
        )

    with c4:
        show_kpi(
            "SALES REPRESENTATIVES",
            str(total_reps),
            "👥",
            "#EA580C,#FB923C",
            "Active scorecard records"
        )

    st.markdown(" ")

    # CHART SECTION

    left, right = st.columns(2)

    with left:

        section_title(
            "📊 Representative Revenue",
            "Revenue generated by sales representatives"
        )

        if not rep_df.empty:

            rep_col = find_col(
                rep_df, "rep_name"
            ) or find_col(rep_df, "rep_id")

            revenue_col = find_col(
                rep_df, "won_revenue"
            )

            if rep_col and revenue_col:

                chart_data = rep_df.copy()

                chart_data = chart_data.sort_values(
                    revenue_col,
                    ascending=False
                ).head(10)

                fig = px.bar(
                    chart_data,
                    x=rep_col,
                    y=revenue_col,
                    color=revenue_col,
                    color_continuous_scale="Blues",
                    title="Top 10 Representatives"
                )

                fig.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False
                )

                st.plotly_chart(
                    make_chart(fig),
                    use_container_width=True
                )

            else:
                st.info("Revenue columns unavailable.")

        else:
            st.warning("Representative data not found.")

    with right:

        section_title(
            "🌍 Territory Performance",
            "Compare sales performance across territories"
        )

        if not territory_df.empty:

            territory_col = find_col(
                territory_df, "territory_name"
            ) or find_col(
                territory_df, "territory_id"
            )

            numeric_cols = territory_df.select_dtypes(
                include="number"
            ).columns.tolist()

            if territory_col and numeric_cols:

                metric = st.selectbox(
                    "Select metric",
                    numeric_cols,
                    key="overview_metric"
                )

                fig = px.bar(
                    territory_df,
                    x=territory_col,
                    y=metric,
                    color=metric,
                    color_continuous_scale="Purples"
                )

                fig.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False
                )

                st.plotly_chart(
                    make_chart(fig),
                    use_container_width=True
                )

            else:
                st.info("Territory columns unavailable.")

        else:
            st.warning("Territory data not found.")

    # TOP PERFORMERS

    section_title(
        "🏆 Top Performing Representatives",
        "Representatives ranked by won revenue"
    )

    if not rep_df.empty:

        revenue_col = find_col(
            rep_df, "won_revenue"
        )

        if revenue_col:

            st.dataframe(
                rep_df.sort_values(
                    revenue_col,
                    ascending=False
                ).head(10),
                use_container_width=True,
                hide_index=True
            )


# =====================================================
# REPRESENTATIVES
# =====================================================

elif page == "👥 Representatives":

    st.title("Sales Representatives")

    st.caption(
        "Analyze individual sales performance and win rates."
    )

    if not rep_df.empty:

        search = st.text_input(
            "🔍 Search Representative",
            placeholder="Enter representative ID or name"
        )

        filtered = rep_df.copy()

        if search:

            mask = filtered.astype(str).apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False
                )
            ).any(axis=1)

            filtered = filtered[mask]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        rep_col = find_col(
            filtered, "rep_id"
        )

        win_col = find_col(
            filtered, "win_rate"
        )

        if rep_col and win_col:

            fig = px.bar(
                filtered,
                x=rep_col,
                y=win_col,
                color=win_col,
                color_continuous_scale="Viridis",
                title="Representative Win Rate"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                make_chart(fig, 430),
                use_container_width=True
            )

    else:

        st.warning("Representative scorecard not found.")


# =====================================================
# TERRITORY ANALYSIS
# =====================================================

elif page == "🌍 Territories":

    st.title("Territory Analytics")

    st.caption(
        "Compare territory-level business performance."
    )

    if not territory_df.empty:

        st.dataframe(
            territory_df,
            use_container_width=True,
            hide_index=True
        )

        territory_col = find_col(
            territory_df, "territory_name"
        ) or find_col(
            territory_df, "territory_id"
        )

        numeric_cols = territory_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if territory_col and numeric_cols:

            metric = st.selectbox(
                "Choose performance metric",
                numeric_cols
            )

            fig = px.bar(
                territory_df,
                x=territory_col,
                y=metric,
                color=metric,
                color_continuous_scale="Plasma",
                title="Territory Comparison"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                make_chart(fig, 450),
                use_container_width=True
            )

    else:

        st.warning("Territory report not available.")


# =====================================================
# PIPELINE ANALYSIS
# =====================================================

elif page == "📈 Pipeline Analysis":

    st.title("Pipeline & Deal Health")

    st.caption(
        "Monitor opportunities, sales stages and deal quality."
    )

    left, right = st.columns(2)

    with left:

        section_title("📊 Pipeline Summary")

        if not pipeline_df.empty:

            st.dataframe(
                pipeline_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("Pipeline summary not found.")

    with right:

        section_title("❤️ Deal Health")

        if not deal_df.empty:

            st.dataframe(
                deal_df,
                use_container_width=True,
                hide_index=True
            )

            score_col = find_col(
                deal_df, "health_score"
            )

            if score_col:

                fig = px.histogram(
                    deal_df,
                    x=score_col,
                    nbins=12,
                    title="Deal Health Distribution",
                    color_discrete_sequence=["#8B5CF6"]
                )

                st.plotly_chart(
                    make_chart(fig),
                    use_container_width=True
                )

        else:

            st.info("Deal health report not found.")


# =====================================================
# REVENUE FORECAST
# =====================================================

elif page == "🔮 Revenue Forecast":

    st.title("Revenue Forecasting")

    st.caption(
        "Future revenue projections using the Prophet forecasting model."
    )

    if not forecast_df.empty:

        date_col = find_col(
            forecast_df, "ds"
        )

        forecast_col = find_col(
            forecast_df, "yhat"
        )

        lower_col = find_col(
            forecast_df, "yhat_lower"
        )

        upper_col = find_col(
            forecast_df, "yhat_upper"
        )

        if date_col and forecast_col:

            chart_df = forecast_df.copy()

            chart_df[date_col] = pd.to_datetime(
                chart_df[date_col]
            )

            fig = go.Figure()

            # Confidence interval

            if lower_col and upper_col:

                fig.add_trace(
                    go.Scatter(
                        x=chart_df[date_col],
                        y=chart_df[upper_col],
                        mode="lines",
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo="skip"
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=chart_df[date_col],
                        y=chart_df[lower_col],
                        mode="lines",
                        fill="tonexty",
                        fillcolor="rgba(124,58,237,0.12)",
                        line=dict(width=0),
                        name="Forecast Range"
                    )
                )

            fig.add_trace(
                go.Scatter(
                    x=chart_df[date_col],
                    y=chart_df[forecast_col],
                    mode="lines+markers",
                    line=dict(
                        color="#7C3AED",
                        width=3
                    ),
                    marker=dict(size=8),
                    name="Predicted Revenue"
                )
            )

            fig.update_layout(
                title="Revenue Prediction",
                hovermode="x unified"
            )

            st.plotly_chart(
                make_chart(fig, 480),
                use_container_width=True
            )

            section_title("📅 Latest Predictions")

            st.dataframe(
                chart_df.tail(6),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning("Forecast columns are missing.")

    else:

        st.warning("Forecast results not found.")


# =====================================================
# COMMISSION MANAGEMENT
# =====================================================

elif page == "💰 Commission":

    st.title("Commission Management")

    st.caption(
        "Monitor representative commission calculations."
    )

    if not commission_df.empty:

        commission_col = find_col(
            commission_df, "commission"
        )

        if commission_col:

            total = commission_df[
                commission_col
            ].sum()

            avg = commission_df[
                commission_col
            ].mean()

            c1, c2 = st.columns(2)

            c1.metric(
                "Total Commission",
                money(total)
            )

            c2.metric(
                "Average Commission",
                money(avg)
            )

            rep_col = find_col(
                commission_df, "rep_id"
            )

            if rep_col:

                fig = px.bar(
                    commission_df,
                    x=rep_col,
                    y=commission_col,
                    color=commission_col,
                    color_continuous_scale="Sunset",
                    title="Commission by Representative"
                )

                fig.update_layout(
                    coloraxis_showscale=False
                )

                st.plotly_chart(
                    make_chart(fig, 430),
                    use_container_width=True
                )

        st.markdown("### Commission Details")

        st.dataframe(
            commission_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("Commission report not found.")


# =====================================================
# AI SALES COACHING
# =====================================================

elif page == "🤖 AI Coaching":

    st.title("AI Sales Coaching Center")

    st.caption(
        "Review sales coaching reports generated for representatives."
    )

    coaching_files = sorted(
        glob.glob("output/coaching_*.txt")
    )

    if coaching_files:

        rep_options = {
            os.path.basename(f).replace(
                "coaching_", ""
            ).replace(".txt", ""): f
            for f in coaching_files
        }

        selected_rep = st.selectbox(
            "Select Representative",
            list(rep_options.keys())
        )

        selected_file = rep_options[selected_rep]

        with open(
            selected_file,
            "r",
            encoding="utf-8"
        ) as file:

            coaching_text = file.read()

        st.markdown(
            f"""
            <div class="content-card">
                <h3>🤖 Coaching Report: {selected_rep}</h3>
                <p style="color:#475569;">
                    Sales performance coaching and recommendations
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.info(coaching_text)

        st.download_button(
            "⬇ Download Coaching Report",
            data=coaching_text,
            file_name=f"{selected_rep}_coaching.txt",
            mime="text/plain"
        )

    else:

        st.warning(
            "No coaching reports found. Run sales_coach.py first."
        )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px;">

    <h4 style="color:#4338CA;">
        🚀 SalesVision AI
    </h4>

    <p style="color:#64748B; font-size:12px;">
        AgentAI-035 | AI-Powered Sales Management System
        <br>
        Built using Python, Streamlit, XGBoost and Prophet
    </p>

</div>
""", unsafe_allow_html=True)