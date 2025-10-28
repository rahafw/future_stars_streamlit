import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Custom CSS
st.markdown("""
<style>
/* Tabs styling */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    border-bottom: 3px solid #84A98C !important;
    color: #84A98C !important;
    font-weight: bold;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
    color: #CAD2C5 !important;
}

/* Sidebar */
[data-testid="stSidebar"] { min-width: 280px; max-width: 320px; background:#23343a; }
[data-testid="stSidebar"] * { color: #CAD2C5 !important; }

/* Slider handle only */
.stSlider [role="slider"] {
    background: #84A98C !important;
    border: 2px solid #84A98C !important;
}

/* KPI Grid */
.kpi-grid{
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 20px;
  height: 100%;
}

/* KPI Card */
.kpi-card{
  background: linear-gradient(145deg, #2F3E46, #354F52);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.35);
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center;
}
.kpi-title{ font-size:14px; color:#CAD2C5; opacity:.9; margin-bottom:6px; }
.kpi-value{ font-size:26px; font-weight:800; color:#84A98C; }
.kpi-sub{ font-size:12px; color:#CAD2C5; opacity:.7; margin-top:4px; }

/* Top Future Star Card */
.top-card{
  background: linear-gradient(145deg, #2F3E46, #354F52);
  border-radius: 20px;
  padding: 30px;
  height: 100%;
  box-shadow: 0 8px 20px rgba(0,0,0,0.35);
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  text-align: center;
}
.top-name{ font-size:28px; font-weight:800; color:#84A98C; margin-bottom:15px; }
.top-line{ font-size:18px; opacity:.85; margin-bottom:10px; color:#CAD2C5; }
.top-prob{ font-size:26px; font-weight:700; color:#84A98C; margin-bottom:10px; }
.top-metric{ font-size:16px; color:#CAD2C5; opacity:.8; }
</style>
""", unsafe_allow_html=True)


# Settings

API_URL = "https://future-stars-127911851563.europe-west1.run.app"
earthy_colors = {
    "light": "#CAD2C5",
    "green": "#84A98C",
    "teal": "#52796F",
    "deep": "#354F52",
    "dark": "#2F3E46"
}

st.set_page_config(page_title="Future Stars", layout="wide")


# Navigation
page = st.sidebar.radio("Navigation", ["Predict Player", "Analysis Dashboard"])

# Page 1: Predict Player
if page == "Predict Player":
    st.markdown("# Are You the Next Future Star")
    st.markdown("Welcome to the **Future Stars Talent Predictor**! Enter your details below to check your potential.")
    st.markdown("---")

    st.subheader("Player Input")
    with st.form("player_form"):
        col1, col2, col3 = st.columns(3)
        player_name = col1.text_input("Player Name", placeholder="Enter your name")
        age = col2.number_input("Age", max_value=45)
        positions = ["GK", "DF", "MF", "FW"]
        pos = col3.selectbox("Position", ["Select a Position"] + positions, index=0)

        col4, col5, col6 = st.columns(3)
        minutes = col4.number_input("Minutes Played", min_value=0)
        ga = col5.number_input("Goals + Assists", min_value=0)
        xg = col6.number_input("Expected Goals (xG)", min_value=0.0, step=0.1)

        col7, col8, col9 = st.columns(3)
        xag = col7.number_input("Expected Assists (xAG)", min_value=0.0, step=0.1)
        prog_pass = col8.number_input("Progressive Passes", min_value=0)
        save_pct = col9.number_input("Save % (GK only)", min_value=0.0, max_value=1.0, step=0.01)

        col10, col11, col12 = st.columns(3)
        tackles = col10.number_input("Tackles", min_value=0)
        blocks = col11.number_input("Blocks", min_value=0)
        clearances = col12.number_input("Clearances", min_value=0)

        nationality = st.text_input("Nationality", placeholder="Enter your nationality")

        # Centered button
        b1, b2, b3 = st.columns([2,1,2])
        with b2:
            submitted = st.form_submit_button("Predict")

    if submitted:
        payload = {
            "player_name": player_name,
            "position": pos,
            "nationality": nationality,
            "age": age,
            "minutes_played": minutes,
            "goals_assists": ga,
            "expected_goals": xg,
            "expected_assists": xag,
            "tackles": tackles,
            "blocks": blocks,
            "clearances": clearances,
            "progressive_passes": prog_pass,
            "save_percent": save_pct
        }
        with st.spinner("Contacting Future Stars API..."):
            response = requests.post(f"{API_URL}/predict_one", json=payload)
        if response.status_code == 200:
            st.success("Prediction Complete")
            df_result = pd.DataFrame([response.json()])
            if "Probability" in df_result.columns:
                df_result["Probability"] = (
                    df_result["Probability"].astype(str).str.replace("%", "", regex=False)
                )
                df_result["Probability"] = pd.to_numeric(df_result["Probability"], errors="coerce")
            st.write(df_result)
        else:
            st.error(f"API Error {response.status_code}: {response.text}")

    # CSV Upload
    st.markdown("---")
    st.subheader("Or upload a CSV file for multiple players")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        st.success("File uploaded successfully!")

        if st.button("Show Analysis"):
            files = {"file": ("players.csv", uploaded_file.getvalue(), "text/csv")}
            with st.spinner("Processing..."):
                r = requests.post(f"{API_URL}/predict_file", files=files, timeout=60)
            if r.status_code == 200:
                df_pred = pd.DataFrame(r.json())
                if "Probability" in df_pred.columns:
                    df_pred["Probability"] = (
                        df_pred["Probability"].astype(str).str.replace("%", "", regex=False)
                    )
                    df_pred["Probability"] = pd.to_numeric(df_pred["Probability"], errors="coerce")
                elif "probability" in df_pred.columns:
                    df_pred["Probability"] = (df_pred["probability"].astype(float) * 100).round(2)
                if "prediction" in df_pred.columns:
                    df_pred["Prediction"] = df_pred["prediction"]
                st.session_state["analysis_df"] = df_pred
                st.session_state["page"] = "Analysis Dashboard"
                st.success("Predictions ready! Switch to Analysis Dashboard.")
            else:
                st.error(f"API Error {r.status_code}: {r.text}")


# Page 2: Analysis Dashboard
if page == "Analysis Dashboard":
    st.title("Analysis Dashboard")

    if "analysis_df" in st.session_state:
        df = st.session_state["analysis_df"]

        if "Probability" in df.columns:
            df["Probability"] = df["Probability"].astype(str).str.replace("%", "", regex=False)
            df["Probability"] = pd.to_numeric(df["Probability"], errors="coerce")
        elif "probability" in df.columns:
            df["Probability"] = (df["probability"].astype(float) * 100).round(2)

        # Sidebar Filters
        with st.sidebar:
            st.markdown("### Filters")
            pos_options = sorted(df["Pos"].dropna().unique().tolist())
            pred_options = sorted(df["Prediction"].dropna().unique().tolist())
            pos_filter = st.multiselect("Position", pos_options, default=pos_options)
            pred_filter = st.multiselect("Prediction", pred_options, default=pred_options)
            age_range = st.slider("Age Range", int(df["Age"].min()), int(df["Age"].max()), (18,30))
            prob_range = st.slider("Probability (%)", 0.0, 100.0, (0.0,100.0))

        # Apply filters
        fdf = df.copy()
        fdf = fdf[fdf["Pos"].isin(pos_filter)]
        fdf = fdf[fdf["Prediction"].isin(pred_filter)]
        fdf = fdf[(fdf["Age"].between(age_range[0], age_range[1]))]
        fdf = fdf[(fdf["Probability"].between(prob_range[0], prob_range[1]))]

        # Tabs
        tab1, tab2 = st.tabs(["Visual Analysis", "All Players Stats"])

        with tab1:
            # Row 1: KPI Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Age AVG", round(df["Age"].mean(), 1))
            c2.metric("Total Players", len(df))
            c3.metric("Avg Probability", f"{df['Probability'].mean():.2f}%")
            c4.metric("Future Stars %", f"{(df['Prediction'].eq('Future Star').mean()*100):.1f}%")

            st.markdown("---")

            # Row 2: Top Future Star full width
            left_col, right_col = st.columns([1,2])

            # Left: Top Future Star Card
            if not fdf.empty:
                top_player = fdf.sort_values("Probability", ascending=False).iloc[0]
                left_col.markdown(
                    f"""
                    <div class="top-card" style="height: 400px; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:20px; font-weight:700; color:#CAD2C5; margin-bottom:12px; text-transform:uppercase; letter-spacing:1px;">
                            Top Future Star
                        </div>
                        <div class="top-name">{top_player['Player']}</div>
                        <div class="top-line">{top_player['Pos']} | {int(top_player['Age'])} yrs</div>
                        <div class="top-prob">{top_player['Probability']:.2f}%</div>
                        <div class="top-metric">{top_player['Key Metric']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # Right: Grouped Bar Chart
            by_pos_pred = fdf.groupby(["Pos","Prediction"]).size().reset_index(name="Count")
            fig1 = px.bar(
                by_pos_pred, x="Pos", y="Count", color="Prediction", barmode="group",
                title="Future Stars vs Not Future Stars by Position",
                color_discrete_sequence=[earthy_colors["green"], earthy_colors["teal"]]
            )
            fig1.update_layout(
                plot_bgcolor=earthy_colors["dark"],
                paper_bgcolor=earthy_colors["dark"],
                font=dict(color=earthy_colors["light"])
            )
            right_col.plotly_chart(fig1, use_container_width=True)

            # --- Row 3: Top 5 Bar Chart + Radar ---
            row3_col1, row3_col2 = st.columns([1.2, 1])  # adjust width ratio if needed

            # Column 1: Top 5 Bar Chart
            with row3_col1:
                if not fdf.empty:
                    top5 = fdf.sort_values("Probability", ascending=False).head(5)

                    fig_bar = px.bar(
                        top5,
                        x="Probability",
                        y="Player",
                        orientation="h",
                        text="Probability",
                        title="Top 5 Future Stars by Probability",
                        color_discrete_sequence=[earthy_colors["green"]]
                    )
                    fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                    fig_bar.update_layout(
                        xaxis_title="Probability (%)",
                        yaxis_title="",
                        yaxis=dict(autorange="reversed"),
                        height=400
                    )

                    st.plotly_chart(fig_bar, use_container_width=True)

            # Column 2: Radar Chart for Top Future Star
            with row3_col2:
                if not fdf.empty:
                    fig_scatter = px.scatter(
                        fdf,
                        x="Age",
                        y="Probability",
                        color="Prediction",
                        hover_name="Player",
                        title="Age vs Probability",
                        size="Probability",
                        color_discrete_sequence=[earthy_colors["green"], earthy_colors["teal"]]
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)


        with tab2:
            st.markdown("### All Players Stats")
            st.dataframe(fdf, use_container_width=True)

    else:
        st.warning("No predictions loaded yet. Please upload CSV on 'Predict Player' page.")
