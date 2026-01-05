import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/dashboard/macro_long_dashboard.parquet")
OUT_DIR = Path("outputs/eda")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_parquet(DATA_PATH)

    # ------------------ 1) STATISTIQUES DESCRIPTIVES ------------------
    desc = (
        df.dropna(subset=["value"])
          .groupby(["indicator_name", "region_group"])
          .agg(
              mean=("value", "mean"),
              median=("value", "median"),
              std=("value", "std"),
              min=("value", "min"),
              max=("value", "max"),
          )
          .reset_index()
    )

    desc.to_csv(OUT_DIR / "stats_by_indicator_region.csv", index=False)

    # ------------------ 2) MOYENNES PAR PAYS (2000–2024) ------------------
    avg_country = (
        df.dropna(subset=["value"])
          .groupby(["iso3", "country", "region_group", "indicator_name"])
          .agg(avg_value=("value", "mean"))
          .reset_index()
    )

    avg_country.to_csv(OUT_DIR / "avg_by_country_indicator.csv", index=False)

    # ------------------ 3) EVOLUTION TEMPORELLE (MOYENNES REGIONALES) ------------------
    regional_trend = (
        df.dropna(subset=["value"])
          .groupby(["region_group", "indicator_name", "year"])
          .agg(mean_value=("value", "mean"))
          .reset_index()
    )

    regional_trend.to_csv(OUT_DIR / "regional_trends.csv", index=False)

    # ------------------ 4) CORRELATIONS SIMPLES (WIDE) ------------------
    wide = pd.read_parquet("data/processed/dashboard/macro_wide_dashboard.parquet")

    corr = (
        wide[[
            "GDP_Growth_pct",
            "Inflation_pct",
            "Unemployment_pct",
            "Public_debt_pct_GDP"
        ]]
        .corr()
    )

    corr.to_csv(OUT_DIR / "macro_correlations.csv")

    print("✅ Analyse exploratoire terminée")
    print("Fichiers générés dans outputs/eda/")
    print("\nAperçu stats régionales:")
    print(desc.head(10))
    print("\nCorrélations macro:")
    print(corr)

if __name__ == "__main__":
    main()
