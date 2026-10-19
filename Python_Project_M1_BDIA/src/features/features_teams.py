# src/features/features_teams.py

import os
import pandas as pd

# Dictionnaire des abréviations (comme tu l'as demandé)
ABBREVIATIONS = {
    "Atlanta Hawks": "ATL",
    "St. Louis Hawks": "STL",
    "Milwaukee Hawks": "MLH",
    "Tri-Cities Blackhawks": "TRI",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "New Jersey Nets": "NJN",
    "New York Nets": "NYN",
    "New Jersey Americans": "NYA",
    "Charlotte Hornets": "CHA",
    "Charlotte Bobcats": "CHB",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Denver Rockets": "DNR",
    "Detroit Pistons": "DET",
    "Fort Wayne Pistons": "FWP",
    "Golden State Warriors": "GSW",
    "San Francisco Warriors": "SFW",
    "Philadelphia Warriors": "PHW",
    "Houston Rockets": "HOU",
    "San Diego Rockets": "SDR",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "San Diego Clippers": "SDC",
    "Buffalo Braves": "BUF",
    "Los Angeles Lakers": "LAL",
    "Minneapolis Lakers": "MNL",
    "Memphis Grizzlies": "MEM",
    "Vancouver Grizzlies": "VAN",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New Orleans Hornets": "NOH",
    "NO/Ok. City Hornets": "NOK",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Seattle SuperSonics": "SEA",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Syracuse Nationals": "SYR",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "Kansas City Kings": "KCK",
    "Kansas City-Omaha Kings": "KCO",
    "Cincinnati Royals": "CIN",
    "Rochester Royals": "ROR",
    "San Antonio Spurs": "SAS",
    "Texas Chaparrals": "TEX",
    "Dallas Chaparrals": "DAA",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "New Orleans Jazz": "NOJ",
    "Washington Wizards": "WAS",
    "Washington Bullets": "WSB",
    "Capital Bullets": "CAP",
    "Baltimore Bullets": "BAL",
    "Chicago Zephyrs": "CHI-Z",
    "Chicago Packers": "CHI-P"
}

class TeamsFeatureEngineer:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Fichier introuvable : {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        print(f"Chargement de {len(self.df):,} lignes de franchises historiques")
        return self  # OBLIGATOIRE

    def create_team_features(self):
        print("Création des features par franchise + abréviations...")

        # Ajouter l'abréviation
        self.df["Abbreviation"] = self.df["Franchise_clean"].map(ABBREVIATIONS).fillna("UNK")

        # Agrégation par franchise actuelle (Team)
        df_agg = self.df.groupby("Team").agg({
            "Yrs": "sum",
            "G": "sum",
            "W": "sum",
            "L": "sum",
            "Plyfs": "sum",
            "Div": "sum",
            "Conf": "sum",
            "Champ": "sum",
            "From_year": "min",
            "To_year": "max",
            "Abbreviation": "first"
        }).reset_index()

        # Features
        df_agg["Age"] = 2025 - df_agg["From_year"]
        df_agg["AllTime_WinRate"] = df_agg["W"] / (df_agg["W"] + df_agg["L"])
        df_agg["Playoff_Rate"] = df_agg["Plyfs"] / df_agg["Yrs"]
        df_agg["Champ_Rate"] = df_agg["Champ"] / df_agg["Yrs"]
        df_agg["Finals_Rate"] = df_agg["Conf"] / df_agg["Yrs"]
        df_agg["Has_Relocated"] = self.df.groupby("Team")["Franchise_clean"].nunique().gt(1).astype(int).values
        df_agg["ABA_Origin"] = self.df.groupby("Team")["Lg"].apply(lambda x: "ABA" in x.values).astype(int).values

        self.df = df_agg
        print(f"Features créées pour {len(self.df)} franchises")
        return self  # OBLIGATOIRE

    def finalize(self):
        print("Finalisation du dataset franchises...")
        self.df = self.df.sort_values("AllTime_WinRate", ascending=False).reset_index(drop=True)
        return self  # OBLIGATOIRE

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f"\nFEATURE ENGINEERING FRANCHISES TERMINÉ !")
        print(f"Fichier : {self.output_path}")
        print("\nTop 5 :")
        print(self.df[["Team", "Abbreviation", "Champ", "AllTime_WinRate"]].head())
        return self  # OBLIGATOIRE


if __name__ == "__main__":
    TeamsFeatureEngineer(
        "data/cleaned/teams/nba_teams_clean.csv",
        "data/features/nba_teams_features.csv"
    ).load().create_team_features().finalize().save()