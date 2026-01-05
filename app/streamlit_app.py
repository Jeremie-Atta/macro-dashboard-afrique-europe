import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path

DATA_PATH = Path("data/processed/dashboard/macro_long_dashboard.parquet")

st.set_page_config(
    page_title="Dashboard macro — Afrique vs Europe",
    page_icon="📊",
    layout="wide",
)

@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_PATH)
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

# -------------------- SIDEBAR --------------------
st.sidebar.title("Filtres")

all_countries = sorted(df["country"].unique().tolist())
all_indicators = sorted(df["indicator_name"].unique().tolist())
min_year, max_year = int(df["year"].min()), int(df["year"].max())

selected_countries = st.sidebar.multiselect(
    "Pays",
    options=all_countries,
    default=[c for c in all_countries if c in ["Côte d'Ivoire", "France", "Ghana", "Allemagne"]][:4]
)

selected_indicator = st.sidebar.selectbox(
    "Indicateur",
    options=all_indicators,
    index=all_indicators.index("GDP_Growth_pct") if "GDP_Growth_pct" in all_indicators else 0
)

year_range = st.sidebar.slider(
    "Période",
    min_value=min_year,
    max_value=max_year,
    value=(max(min_year, 2000), max_year)
)

group_view = st.sidebar.checkbox("Afficher moyenne par région (Afrique vs Europe)", value=True)

# -------------------- FORMATS (unités + affichage) --------------------
FORMAT = {
    "GDP_USD": {"suffix": " USD", "fmt": ",.0f"},
    "GDP_per_capita_USD": {"suffix": " USD", "fmt": ",.0f"},
    "GDP_Growth_pct": {"suffix": " %", "fmt": ",.2f"},
    "Inflation_pct": {"suffix": " %", "fmt": ",.2f"},
    "Unemployment_pct": {"suffix": " %", "fmt": ",.2f"},
    "Public_debt_pct_GDP": {"suffix": " % du PIB", "fmt": ",.2f"},
}
cfg = FORMAT.get(selected_indicator, {"suffix": "", "fmt": ",.2f"})

# -------------------- FILTER DATA --------------------
dff = df[
    (df["country"].isin(selected_countries)) &
    (df["indicator_name"] == selected_indicator) &
    (df["year"].between(year_range[0], year_range[1]))
].copy()

if dff.empty:
    st.warning("Aucune donnée pour ces filtres. Essaie un autre pays/indicateur/période.")
    st.stop()

# -------------------- HEADER --------------------
st.title("📊 Dashboard macroéconomique comparatif")
st.caption("Source: World Bank Open Data — données nettoyées & structurées (format long).")

# -------------------- SYNTHÈSE RÉGIONALE --------------------
st.subheader("Synthèse régionale sur la période sélectionnée")

region_summary = (
    df[(df["indicator_name"] == selected_indicator) &
       (df["year"].between(year_range[0], year_range[1]))]
    .dropna(subset=["value"])
    .groupby("region_group", as_index=False)
    .agg(mean_value=("value", "mean"))
)

c1, c2 = st.columns(2)
for col, reg in [(c1, "Afrique"), (c2, "Europe")]:
    val = region_summary.loc[region_summary["region_group"] == reg, "mean_value"]
    with col:
        st.metric(
            f"Moyenne {reg}",
            "NA" if val.empty else f"{float(val.iloc[0]):{cfg['fmt']}}{cfg['suffix']}"
        )

# -------------------- KPI ROW --------------------
def latest_value(sub_df: pd.DataFrame):
    tmp = sub_df.dropna(subset=["value"]).sort_values("year")
    if tmp.empty:
        return None, None
    last = tmp.iloc[-1]
    prev = tmp.iloc[-2] if len(tmp) >= 2 else None
    delta = None if prev is None else (last["value"] - prev["value"])
    return float(last["value"]), (None if delta is None else float(delta))

kpi_cols = st.columns(min(4, len(selected_countries)))
for i, country in enumerate(selected_countries[:len(kpi_cols)]):
    v, d = latest_value(dff[dff["country"] == country])
    with kpi_cols[i]:
        if v is None:
            st.metric(country, "NA")
        else:
            st.metric(
                country,
                f"{v:{cfg['fmt']}}{cfg['suffix']}",
                None if d is None else f"{d:+.2f}"
            )

# -------------------- MAIN CHART --------------------
st.subheader(f"Évolution — {selected_indicator}")

line = (
    alt.Chart(dff)
    .mark_line()
    .encode(
        x=alt.X("year:O", title="Année"),
        y=alt.Y("value:Q", title=f"{selected_indicator}{cfg['suffix']}"),
        color=alt.Color("country:N", title="Pays"),
        tooltip=[
            "country:N",
            "year:O",
            alt.Tooltip("value:Q", format=cfg["fmt"])
        ]
    )
    .properties(height=380)
)

st.altair_chart(line, use_container_width=True)

# -------------------- REGIONAL AVERAGES --------------------
if group_view:
    st.subheader("Moyenne régionale (Afrique vs Europe)")
    region_df = df[
        (df["indicator_name"] == selected_indicator) &
        (df["year"].between(year_range[0], year_range[1]))
    ].dropna(subset=["value"]).copy()

    region_mean = (
        region_df.groupby(["region_group", "year"], as_index=False)
        .agg(mean_value=("value", "mean"))
    )

    region_chart = (
        alt.Chart(region_mean)
        .mark_line()
        .encode(
            x=alt.X("year:O", title="Année"),
            y=alt.Y("mean_value:Q", title=f"{selected_indicator} (moyenne){cfg['suffix']}"),
            color=alt.Color("region_group:N", title="Région"),
            tooltip=[
                "region_group:N",
                "year:O",
                alt.Tooltip("mean_value:Q", format=cfg["fmt"])
            ]
        )
        .properties(height=300)
    )
    st.altair_chart(region_chart, use_container_width=True)

# -------------------- RANKING --------------------
st.subheader("Classement (moyenne sur la période sélectionnée)")

rank_df = (
    df[(df["indicator_name"] == selected_indicator) &
       (df["year"].between(year_range[0], year_range[1]))]
    .groupby(["country"], as_index=False)
    .agg(avg_value=("value", "mean"))
    .dropna()
    .sort_values("avg_value", ascending=False)
)

bar = (
    alt.Chart(rank_df)
    .mark_bar()
    .encode(
        y=alt.Y("country:N", sort="-x", title="Pays"),
        x=alt.X("avg_value:Q", title=f"Moyenne ({year_range[0]}–{year_range[1]}){cfg['suffix']}"),
        tooltip=["country:N", alt.Tooltip("avg_value:Q", format=cfg["fmt"])]
    )
    .properties(height=min(600, 28 * len(rank_df) + 60))
)

st.altair_chart(bar, use_container_width=True)

# -------------------- INSIGHTS --------------------
st.subheader("Insights (automatiques)")

vol = (
    dff.dropna(subset=["value"])
       .groupby("country", as_index=False)
       .agg(std=("value", "std"), mean=("value", "mean"))
)

most_volatile = vol.sort_values("std", ascending=False).head(1) if not vol.empty else pd.DataFrame()
most_stable = vol.sort_values("std", ascending=True).head(1) if not vol.empty else pd.DataFrame()

bullets = []
if not most_volatile.empty:
    bullets.append(f"• Pays le plus volatil sur la période: **{most_volatile.iloc[0]['country']}**.")
if not most_stable.empty:
    bullets.append(f"• Pays le plus stable sur la période: **{most_stable.iloc[0]['country']}**.")

if not rank_df.empty:
    best = rank_df.iloc[0]
    worst = rank_df.iloc[-1]
    bullets.append(f"• Plus haut niveau moyen: **{best['country']}** ({best['avg_value']:{cfg['fmt']}}{cfg['suffix']}).")
    bullets.append(f"• Plus bas niveau moyen: **{worst['country']}** ({worst['avg_value']:{cfg['fmt']}}{cfg['suffix']}).")

st.write("\n".join(bullets) if bullets else "Pas assez de données pour générer des insights.")

# -------------------- DATA DOWNLOAD --------------------
st.subheader("Télécharger les données filtrées")
csv_bytes = dff.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Télécharger (CSV)",
    data=csv_bytes,
    file_name=f"macro_{selected_indicator}_{year_range[0]}_{year_range[1]}.csv",
    mime="text/csv"
)

with st.expander("Voir les données (aperçu)"):
    st.dataframe(dff.sort_values(["country", "year"]), use_container_width=True)
