import time
import requests
import pandas as pd

def fetch_world_bank_indicator(country_iso3: str, indicator: str, per_page: int = 20000) -> pd.DataFrame:
    url = f"https://api.worldbank.org/v2/country/{country_iso3}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        # pas d'erreur bloquante: on renvoie un DF vide
        return pd.DataFrame(columns=["country", "iso3", "year", "indicator", "value"])

    rows = []
    for item in data[1]:
        if item is None:
            continue
        # certaines entrées peuvent être incomplètes
        year_str = item.get("date")
        if year_str is None:
            continue

        rows.append({
            "country": item.get("country", {}).get("value"),
            "iso3": country_iso3,
            "year": int(year_str),
            "indicator": indicator,
            "value": item.get("value")
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    # ------------------ PARAMÈTRES ------------------
    countries = {
        # Afrique
        "CIV": "Côte d'Ivoire",
        "SEN": "Sénégal",
        "GHA": "Ghana",
        "KEN": "Kenya",
        "ZAF": "Afrique du Sud",
        # Europe
        "FRA": "France",
        "DEU": "Allemagne",
        "ITA": "Italie",
        "ESP": "Espagne",
        "GBR": "Royaume-Uni",
    }

    indicators = {
        "NY.GDP.MKTP.CD": "GDP_USD",
        "NY.GDP.MKTP.KD.ZG": "GDP_Growth_pct",
        "NY.GDP.PCAP.CD": "GDP_per_capita_USD",
        "FP.CPI.TOTL.ZG": "Inflation_pct",
        "SL.UEM.TOTL.ZS": "Unemployment_pct",
        "GC.DOD.TOTL.GD.ZS": "Public_debt_pct_GDP",
    }

    start_year = 2000
    out_path = "data/raw/world_bank_macro_long_raw.csv"

    # ------------------ COLLECTE ------------------
    all_parts = []
    total_calls = len(countries) * len(indicators)
    call_n = 0

    for iso3 in countries.keys():
        for ind_code in indicators.keys():
            call_n += 1
            print(f"[{call_n}/{total_calls}] Download {iso3} / {ind_code} ...")

            df_part = fetch_world_bank_indicator(iso3, ind_code)
            if not df_part.empty:
                all_parts.append(df_part)

            # petite pause pour éviter de marteler l'API
            time.sleep(0.2)

    if not all_parts:
        raise RuntimeError("Aucune donnée récupérée. Vérifie la connexion internet.")

    df = pd.concat(all_parts, ignore_index=True)

    # ------------------ FILTRAGE + ENRICHISSEMENT ------------------
    df = df[df["year"] >= start_year].copy()
    df["indicator_name"] = df["indicator"].map(indicators)
    df["region_group"] = df["iso3"].apply(lambda x: "Afrique" if x in ["CIV","SEN","GHA","KEN","ZAF"] else "Europe")

    # tri
    df = df.sort_values(["iso3", "indicator", "year"])

    # ------------------ SAUVEGARDE ------------------
    df.to_csv(out_path, index=False)
    print(f"✅ Terminé. Fichier créé -> {out_path}")
    print(df.head(10))
