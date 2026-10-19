# src/features/features_boxscores.py

import os
import pandas as pd

class BoxscoreFeatureEngineer:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Fichier introuvable : {self.input_path}")
        
        self.df = pd.read_csv(self.input_path)
        self.df["Date"] = pd.to_datetime(self.df["Date"], format="%d/%m/%Y")
        self.df = self.df.sort_values("Date").reset_index(drop=True)
        print(f"Chargement de {len(self.df):,} matchs nettoyés")
        return self  # AJOUTÉ (pour chaînage)

    def create_team_features(self):
        print("Création des rolling stats par équipe (10 derniers matchs)...")

        # Créer un dataframe avec une ligne par équipe par match
        home = self.df[["Date", "HomeTeam", "HomePts", "AwayPts"]].rename(
            columns={"HomeTeam": "Team", "HomePts": "Pts", "AwayPts": "OppPts"}
        )
        away = self.df[["Date", "AwayTeam", "AwayPts", "HomePts"]].rename(
            columns={"AwayTeam": "Team", "AwayPts": "Pts", "HomePts": "OppPts"}
        )
        home["IsHome"] = 1
        away["IsHome"] = 0

        games = pd.concat([home, away], ignore_index=True)
        games = games.sort_values(["Team", "Date"])

        # Win / Loss
        games["Win"] = (games["Pts"] > games["OppPts"]).astype(int)

        # Rolling stats sur 10 matchs
        rolling_window = 10
        games["Rolling_PPG"] = games.groupby("Team")["Pts"].transform(
            lambda x: x.rolling(rolling_window, min_periods=1).mean()
        )
        games["Rolling_OPPG"] = games.groupby("Team")["OppPts"].transform(
            lambda x: x.rolling(rolling_window, min_periods=1).mean()
        )
        games["Rolling_PointDiff"] = games["Rolling_PPG"] - games["Rolling_OPPG"]
        games["Rolling_WinRate"] = games.groupby("Team")["Win"].transform(
            lambda x: x.rolling(rolling_window, min_periods=1).mean()
        )

        # Win Streak
        games["ResultShift"] = games.groupby("Team")["Win"].shift()
        games["StreakGroup"] = (games["Win"] != games["ResultShift"]).cumsum()
        games["WinStreak"] = games.groupby(["Team", "StreakGroup"]).cumcount() + 1
        games.loc[games["Win"] == 0, "WinStreak"] *= -1
        games.drop("StreakGroup", axis=1, inplace=True)

        # Jours de repos
        games["PrevDate"] = games.groupby("Team")["Date"].shift(1)
        games["RestDays"] = (games["Date"] - games["PrevDate"]).dt.days.fillna(3).astype(int)

        # Merge back dans le df original
        home_features = games[games["IsHome"] == 1].drop(columns=["IsHome", "ResultShift", "PrevDate"], errors="ignore")
        away_features = games[games["IsHome"] == 0].drop(columns=["IsHome", "ResultShift", "PrevDate"], errors="ignore")

        df_home = self.df.merge(
            home_features.add_prefix("Home_"),
            left_on=["Date", "HomeTeam"],
            right_on=["Home_Date", "Home_Team"],
            how="left"
        )
        df_full = df_home.merge(
            away_features.add_prefix("Away_"),
            left_on=["Date", "AwayTeam"],
            right_on=["Away_Date", "Away_Team"],
            how="left"
        )

        # Nettoyage des colonnes temporaires
        cols_to_drop = [col for col in df_full.columns if "Date_" in col or "Team_" in col]
        df_full.drop(columns=cols_to_drop, errors="ignore", inplace=True)

        self.df = df_full
        return self  # AJOUTÉ

    def create_game_level_features(self):
        print("Création des features de match...")

        self.df["Home_FormAdv"] = self.df["Home_Rolling_WinRate"] - self.df["Away_Rolling_WinRate"]
        self.df["Home_PointDiffAdv"] = self.df["Home_Rolling_PointDiff"] - self.df["Away_Rolling_PointDiff"]
        self.df["Home_RestAdv"] = self.df["Home_RestDays"] - self.df["Away_RestDays"]
        self.df["ExpectedPointDiff"] = self.df["Home_Rolling_PointDiff"] - self.df["Away_Rolling_PointDiff"] + 3.0  # Home advantage

        # Target
        self.df["HomeWin"] = (self.df["HomePts"] > self.df["AwayPts"]).astype(int)
        return self  # AJOUTÉ

    def finalize(self):
        print("Finalisation du dataset...")
        initial = len(self.df)
        self.df = self.df.dropna().reset_index(drop=True)
        print(f"Supprimées {initial - len(self.df):,} lignes avec valeurs manquantes")

        # Colonnes finales
        final_cols = [
            "Date", "HomeTeam", "AwayTeam",
            "Home_Rolling_PPG", "Away_Rolling_PPG",
            "Home_Rolling_OPPG", "Away_Rolling_OPPG",
            "Home_Rolling_WinRate", "Away_Rolling_WinRate",
            "Home_Rolling_PointDiff", "Away_Rolling_PointDiff",
            "Home_FormAdv", "Home_PointDiffAdv", "Home_RestAdv",
            "Home_WinStreak", "Away_WinStreak",
            "Home_RestDays", "Away_RestDays",
            "ExpectedPointDiff",
            "HomeWin"  # Target
        ]
        self.df = self.df[final_cols]
        return self  # AJOUTÉ

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f"\nFEATURE ENGINEERING TERMINÉ !")
        print(f"Fichier sauvegardé : {self.output_path}")
        print(f"→ {len(self.df):,} matchs prêts pour le ML !")
        return self  # AJOUTÉ


# ========================================
# Lancement direct
# ========================================
if __name__ == "__main__":
    INPUT = "data/cleaned/boxscores/nba_boxscores_clean.csv"
    OUTPUT = "data/features/nba_boxscores_features.csv"

    engineer = BoxscoreFeatureEngineer(INPUT, OUTPUT)
    engineer.load()
    engineer.create_team_features()
    engineer.create_game_level_features()
    engineer.finalize()
    engineer.save()