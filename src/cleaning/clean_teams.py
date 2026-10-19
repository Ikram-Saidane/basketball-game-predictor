
import os
import pandas as pd


class TeamCleaner:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Fichier teams brut introuvable : {self.input_path}")

        self.df = pd.read_csv(self.input_path)
        print(f"Chargement de {len(self.df)} franchises depuis {self.input_path}")

    def clean(self):
        if self.df is None:
            raise ValueError("DataFrame non chargé – lance .load() d'abord")

        df = self.df.copy()

        # 1. Corriger W/L% : ".493" → 0.493
        print("Correction de la colonne W/L%...")
        df["W/L%"] = df["W/L%"].astype(str).str.replace(r"^\.", "0.", regex=True)
        df["W/L%"] = pd.to_numeric(df["W/L%"], errors="coerce")

        # 2. Séparer From/To (ex: "1949-50" → 1949 et 1950)
        print("Séparation des colonnes From/To...")
        def split_years(val):
            if pd.isna(val) or not isinstance(val, str) or "-" not in val:
                return None, None
            start, end = val.split("-")
            start = int(start)
            end_int = int(end)
            # Logique pour les années à 2 chiffres
            if end_int >= 0 and end_int <= 30:
                end = 2000 + end_int
            else:
                end = 1900 + end_int
            return start, end

        df[["From_year", "To_year"]] = df["From"].apply(
            lambda x: pd.Series(split_years(x))
        )

        # 3. Colonnes numériques
        numeric_cols = ["Yrs", "G", "W", "L", "Plyfs", "Div", "Conf", "Champ"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        # 4. Nettoyer le nom de franchise
        df["Franchise_clean"] = (
            df["Franchise"]
            .str.replace("St\\. ", "St ", regex=True)
            .str.replace(r"\.", "", regex=True)
            .str.strip()
        )

        # 5. Nom standardisé (pour merge facile avec boxscores/players)
        franchise_mapping = {
            "hawks": "Atlanta Hawks",
            "celtics": "Boston Celtics",
            "nets": "Brooklyn Nets",
            "hornets": "Charlotte Hornets",
            "bulls": "Chicago Bulls",
            "cavaliers": "Cleveland Cavaliers",
            "mavericks": "Dallas Mavericks",
            "nuggets": "Denver Nuggets",
            "pistons": "Detroit Pistons",
            "warriors": "Golden State Warriors",
            "rockets": "Houston Rockets",
            "pacers": "Indiana Pacers",
            "clippers": "Los Angeles Clippers",
            "lakers": "Los Angeles Lakers",
            "grizzlies": "Memphis Grizzlies",
            "heat": "Miami Heat",
            "bucks": "Milwaukee Bucks",
            "timberwolves": "Minnesota Timberwolves",
            "pelicans": "New Orleans Pelicans",
            "knicks": "New York Knicks",
            "thunder": "Oklahoma City Thunder",
            "magic": "Orlando Magic",
            "76ers": "Philadelphia 76ers",
            "suns": "Phoenix Suns",
            "trail blazers": "Portland Trail Blazers",
            "kings": "Sacramento Kings",
            "spurs": "San Antonio Spurs",
            "raptors": "Toronto Raptors",
            "jazz": "Utah Jazz",
            "wizards": "Washington Wizards",
            # Anciennes franchises
            "supersonics": "Seattle SuperSonics",
            "bobcats": "Charlotte Bobcats",
            "new jersey nets": "New Jersey Nets",
            "new orleans hornets": "New Orleans Hornets",
        }

        def standardize_name(name):
            name_lower = name.lower()
            for key, full_name in franchise_mapping.items():
                if key in name_lower:
                    return full_name
            return name.strip()

        df["Team"] = df["Franchise"].apply(standardize_name)

        self.df = df
        print(f"Nettoyage teams terminé → {len(self.df)} franchises prêtes")

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False, encoding="utf-8")
        print(f"Fichier teams propre sauvegardé : {self.output_path}")


# ========================================
# Lancement direct
# ========================================
if __name__ == "__main__":
    RAW_TEAMS = "data/raw/teams/nba_teams.csv"
    CLEAN_TEAMS = "data/cleaned/teams/nba_teams_clean.csv"

    cleaner = TeamCleaner(RAW_TEAMS, CLEAN_TEAMS)
    cleaner.load()
    cleaner.clean()
    cleaner.save()
    print("\nTeams nettoyées avec succès !")