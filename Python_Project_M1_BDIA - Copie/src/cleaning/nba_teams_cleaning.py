import pandas as pd

# 1. Charger le dataset (corrigé)
df = pd.read_csv(r"data\raw\teams\nba_teams.csv")

# 2. Nettoyer la colonne W/L% (.493 → 0.493)
df["W/L%"] = df["W/L%"].astype(str).str.replace(".", "0.", 1)
df["W/L%"] = df["W/L%"].astype(float)

# 3. Séparer les colonnes From et To (format "1949-50")
def split_years(val):
    if isinstance(val, str) and "-" in val:
        start, end = val.split("-")
        # correction : "50" devient 1950
        if len(end) == 2:
            end = "19" + end if int(end) > 30 else "20" + end
        return int(start), int(end)
    return None, None

df[["From_year", "To_year"]] = df["From"].apply(lambda x: pd.Series(split_years(x)))

# 4. Convertir les colonnes numériques
numeric_cols = ["Yrs","G","W","L","Plyfs","Div","Conf","Champ"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# 5. Harmoniser les noms de franchises
df["Franchise_clean"] = (
    df["Franchise"]
    .str.replace("St. ", "St ", regex=False)
    .str.replace(".", "", regex=False)
    .str.strip()
)

# 6. Ajouter une colonne franchise standardisée
def clean_franchise_name(name):
    name = name.lower()
    replacements = {
        "hawks": "Hawks",
        "nets": "Nets",
        "hornets": "Hornets",
        "lakers": "Lakers",
        "clippers": "Clippers",
        "grizzlies": "Grizzlies",
        "kings": "Kings",
        "spurs": "Spurs",
        "rockets": "Rockets",
        "warriors": "Warriors",
        "pistons": "Pistons",
        "76ers": "76ers",
        "celtics": "Celtics",
        "raptors": "Raptors",
        "heat": "Heat",
        "knicks": "Knicks",
        "mavericks": "Mavericks",
        "pacers": "Pacers",
        "bulls": "Bulls",
        "bucks": "Bucks",
        "magic": "Magic",
        "thunder": "Thunder",
        "sonics": "SuperSonics",
        "jazz": "Jazz",
        "suns": "Suns",
        "nuggets": "Nuggets",
    }
    for key, val in replacements.items():
        if key in name:
            return val
    return name.title()

df["Franchise_group"] = df["Franchise"].apply(clean_franchise_name)

# 7. Sauvegarder le dataset propre
df.to_csv("nba_teams_clean.csv", index=False)

print("✔ Cleaning terminé ! Fichier : nba_teams_clean.csv")
