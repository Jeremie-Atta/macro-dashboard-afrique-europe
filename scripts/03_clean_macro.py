import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/world_bank_macro_long_raw.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(RAW_PATH)

    # --- colonnes attendues ---
    expected = {"country", "iso3", "year", "indicator", "value", "indicator_name", "region_group"}
    missing_cols = expected - set(df.columns)
    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans le raw: {missing_cols}")

    # --- types ---
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # --- filtrage années ---
    df = df[df["year"].between(2000, 2100, inclusive="both")].copy()

    # --- nettoyage texte ---
    for c in ["country", "iso3", "indicator", "indicator_name", "region_group"]:
        df[c] = df[c].astype(str).str.strip()

    # --- doublons (rare mais possible) ---
    # si doublons exacts, on garde la moyenne (ou 1ère valeur non-nulle)
    df = (
        df.groupby(["iso3", "country", "region_group", "year", "indicator", "indicator_name"], as_index=False)
          .agg(value=("value", "mean"))
    )

    # --- tri ---
    df = df.sort_values(["iso3", "indicator", "year"]).reset_index(drop=True)

    # --- rapport qualité: % manquant par pays/indicateur ---
    quality = (
        df.assign(is_missing=df["value"].isna())
          .groupby(["iso3", "country", "indicator_name"], as_index=False)
          .agg(
              min_year=("year", "min"),
              max_year=("year", "max"),
              n_years=("year", "nunique"),
              missing_count=("is_missing", "sum"),
              missing_rate=("is_missing", "mean"),
          )
          .sort_values(["missing_rate", "n_years"], ascending=[False, True])
    )

    # --- sauvegardes ---
    out_csv = OUT_DIR / "macro_clean_long.csv"
    out_parquet = OUT_DIR / "macro_clean_long.parquet"
    out_quality = OUT_DIR / "macro_quality_report.csv"

    df.to_csv(out_csv, index=False)
    df.to_parquet(out_parquet, index=False)
    quality.to_csv(out_quality, index=False)

    print("✅ Nettoyage terminé")
    print(f"- Dataset clean (csv)     : {out_csv}")
    print(f"- Dataset clean (parquet) : {out_parquet}")
    print(f"- Rapport qualité         : {out_quality}")
    print("\nAperçu dataset:")
    print(df.head(10))
    print("\nTop 10 séries les plus incomplètes:")
    print(quality.head(10))

if __name__ == "__main__":
    main()
