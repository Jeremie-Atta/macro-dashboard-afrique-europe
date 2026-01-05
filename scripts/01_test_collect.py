import requests
import pandas as pd

def fetch_world_bank_indicator(country_iso3: str, indicator: str, per_page: int = 20000) -> pd.DataFrame:
    """
    Télécharge une série World Bank (1 pays, 1 indicateur) et renvoie un DataFrame:
    country, iso3, year, indicator, value
    """
    url = f"https://api.worldbank.org/v2/country/{country_iso3}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        raise ValueError(f"Aucune donnée renvoyée par l'API pour {country_iso3} / {indicator}")

    rows = []
    for item in data[1]:
        # item["date"] = année sous forme de string
        year = int(item["date"])
        value = item["value"]
        rows.append({
            "country": item["country"]["value"],
            "iso3": country_iso3,
            "year": year,
            "indicator": indicator,
            "value": value
        })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    # Test minimal : Côte d'Ivoire + inflation
    country = "CIV"
    indicator = "FP.CPI.TOTL.ZG"  # Inflation CPI (%)

    df = fetch_world_bank_indicator(country, indicator)

    # Filtre période
    df = df[df["year"] >= 2000].sort_values("year")

    print(df.head(10))
    df.to_csv("data/raw/test_world_bank_CIV_inflation.csv", index=False)
    print("✅ Test OK : fichier créé -> data/raw/test_world_bank_CIV_inflation.csv")
