import pandas as pd
from pathlib import Path

IN_PATH = Path("data/processed/macro_clean_long.parquet")
OUT_DIR = Path("data/processed/dashboard")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_parquet(IN_PATH)

    # ------------------ 1) LONG (optimisé Streamlit) ------------------
    # Ajout de colonnes utiles
    df_long = df.copy()
    df_long["year"] = df_long["year"].astype(int)

    df_long.to_parquet(OUT_DIR / "macro_long_dashboard.parquet", index=False)
    df_long.to_csv(OUT_DIR / "macro_long_dashboard.csv", index=False)

    # ------------------ 2) WIDE (1 colonne = 1 indicateur) ------------------
    df_wide = (
        df_long
        .pivot_table(
            index=["iso3", "country", "region_group", "year"],
            columns="indicator_name",
            values="value",
            aggfunc="mean"
        )
        .reset_index()
        .sort_values(["iso3", "year"])
    )

    df_wide.to_parquet(OUT_DIR / "macro_wide_dashboard.parquet", index=False)
    df_wide.to_csv(OUT_DIR / "macro_wide_dashboard.csv", index=False)

    # ------------------ 3) Dictionnaire indicateurs ------------------
    indicator_dict = (
        df_long[["indicator", "indicator_name"]]
        .drop_duplicates()
        .sort_values("indicator_name")
        .reset_index(drop=True)
    )

    indicator_dict.to_csv(OUT_DIR / "indicator_dictionary.csv", index=False)

    print("✅ Données dashboard prêtes")
    print("- Long  :", OUT_DIR / "macro_long_dashboard.parquet")
    print("- Wide  :", OUT_DIR / "macro_wide_dashboard.parquet")
    print("- Dict. :", OUT_DIR / "indicator_dictionary.csv")
    print("\nAperçu WIDE:")
    print(df_wide.head(10))

if __name__ == "__main__":
    main()
