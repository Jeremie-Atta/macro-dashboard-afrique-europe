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

st.title("Comparaison")

st.sidebar.header("Filtres (Comparaison)")
all_indicators = sorted(df["indicator_name"].unique().tolist())
min_year, max_year = int(df["year"].min()), int(df["year"].max())

selected_indicator = st.sidebar.selectbox("Indicateur", options=all_indicators)
year_range = st.sidebar.slider("Période", min_value=min_year, max_value=max_year, value=(max(min_year, 2000), max_year))
order_desc = st.sidebar.checkbox("Trier décroissant", value=True)

cfg = FORMAT.get(selected_indicator, {"suffix": "", "fmt": ",.2f"})

rank_df = (
    df[(df["indicator_name"] == selected_indicator) &
       (df["year"].between(year_range[0], year_range[1]))]
    .groupby(["country", "region_group"], as_index=False)
    .agg(avg_value=("value", "mean"))
    .dropna()
    .sort_values("avg_value", ascending=not order_desc)
)

st.subheader("Classement (moyenne sur la période)")
bar = (
    alt.Chart(rank_df)
    .mark_bar()
    .encode(
        y=alt.Y("country:N", sort="-x" if order_desc else "x", title="Pays"),
        x=alt.X("avg_value:Q", title=f"Moyenne ({year_range[0]}–{year_range[1]}){cfg['suffix']}"),
        color=alt.Color("region_group:N", title="Région"),
        tooltip=["country:N", "region_group:N", alt.Tooltip("avg_value:Q", format=cfg["fmt"])]
    )
    .properties(height=min(700, 28 * len(rank_df) + 80))
)
st.altair_chart(bar, use_container_width=True)

with st.expander("Table (moyennes)"):
    st.dataframe(rank_df, use_container_width=True)
