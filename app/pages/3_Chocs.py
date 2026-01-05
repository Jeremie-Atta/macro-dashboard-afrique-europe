import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path

DATA_PATH = Path("data/processed/dashboard/macro_long_dashboard.parquet")

FORMAT = {
    "GDP_USD": {"suffix": " USD", "fmt": ",.0f"},
    "GDP_per_capita_USD": {"suffix": " USD", "fmt": ",.0f"},
    "GDP_Growth_pct": {"suffix": " %", "fmt": ",.2f"},
    "Inflation_pct": {"suffix": " %", "fmt": ",.2f"},
    "Unemployment_pct": {"suffix": " %", "fmt": ",.2f"},
    "Public_debt_pct_GDP": {"suffix": " % du PIB", "fmt": ",.2f"},
}

@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_PATH)
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

st.title("Chocs & ruptures")

st.sidebar.header("Filtres (Chocs)")
all_countries = sorted(df["country"].unique().tolist())
all_indicators = sorted(df["indicator_name"].unique().tolist())
min_year, max_year = int(df["year"].min()), int(df["year"].max())

selected_countries = st.sidebar.multiselect("Pays", options=all_countries, default=all_countries[:4])
selected_indicator = st.sidebar.selectbox("Indicateur", options=all_indicators)
year_range = st.sidebar.slider("Période", min_value=min_year, max_value=max_year, value=(max(min_year, 2000), max_year))

show_shocks = st.sidebar.multiselect(
    "Marqueurs de chocs",
    options=[2009, 2020, 2022],
    default=[2009, 2020, 2022]
)

cfg = FORMAT.get(selected_indicator, {"suffix": "", "fmt": ",.2f"})

dff = df[
    (df["country"].isin(selected_countries)) &
    (df["indicator_name"] == selected_indicator) &
    (df["year"].between(year_range[0], year_range[1]))
].copy()

if dff.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()

base = (
    alt.Chart(dff)
    .mark_line()
    .encode(
        x=alt.X("year:O", title="Année"),
        y=alt.Y("value:Q", title=f"{selected_indicator}{cfg['suffix']}"),
        color=alt.Color("country:N", title="Pays"),
        tooltip=["country:N", "year:O", alt.Tooltip("value:Q", format=cfg["fmt"])]
    )
    .properties(height=420)
)

layers = [base]

# lignes verticales de chocs
if show_shocks:
    shock_df = pd.DataFrame({"year": [str(y) for y in show_shocks]})
    shock_lines = (
        alt.Chart(shock_df)
        .mark_rule()
        .encode(x=alt.X("year:O"))
    )
    layers.append(shock_lines)

chart = alt.layer(*layers)
st.altair_chart(chart, use_container_width=True)

st.caption("Marqueurs : 2009 (crise financière), 2020 (COVID), 2022 (choc inflation/énergie).")
