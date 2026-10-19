
import os
import pandas as pd

class PlayersFeatureEngineer:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load(self):
        """Charge le CSV et ajoute la colonne Season sans supprimer les lignes League Average"""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Fichier introuvable : {self.input_path}")
        
        raw_df = pd.read_csv(self.input_path)
        season_start = 2010
        current_season = f"{season_start}-{season_start+1}"
        seasons = []

        for player in raw_df["Player"]:
            # Si ligne League Average → on incrémente la saison
            if "League Average" in str(player):
                season_start += 1
                current_season = f"{season_start}-{season_start+1}"
            seasons.append(current_season)

        raw_df["Season"] = seasons
        self.df = raw_df.sort_values(["Player", "Age"]).reset_index(drop=True)
        print(f"Chargement de {len(self.df):,} stats de joueurs avec saison assignée")
        return self

    def create_player_features(self):
        """Création des features rolling et progression par joueur"""
        print("Création des features par joueur (rolling stats sur 3 saisons)...")

        # Rolling PPG (points par match)
        self.df["Rolling_PPG"] = (
            self.df.groupby("Player")["PTS"].transform(lambda x: x.rolling(3, min_periods=1).mean()) /
            self.df.groupby("Player")["G"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        )

        # Rolling APG (assists par match)
        self.df["Rolling_APG"] = (
            self.df.groupby("Player")["AST"].transform(lambda x: x.rolling(3, min_periods=1).mean()) /
            self.df.groupby("Player")["G"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        )

        # Rolling RPG (rebonds par match)
        self.df["Rolling_RPG"] = (
            self.df.groupby("Player")["TRB"].transform(lambda x: x.rolling(3, min_periods=1).mean()) /
            self.df.groupby("Player")["G"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        )

        # Rolling 3P% et FG%
        self.df["Rolling_3P%"] = self.df.groupby("Player")["3P%"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        self.df["Rolling_FG%"] = self.df.groupby("Player")["FG%"].transform(lambda x: x.rolling(3, min_periods=1).mean())

        # Progression PPG
        self.df["PPG_Improvement"] = self.df.groupby("Player")["PTS"].pct_change()

        # Target simple : All-Star ?
        self.df["Is_AllStar"] = self.df["Awards"].str.contains("AS", na=False).astype(int)

        print("Features joueurs créées : PPG, APG, RPG, % tirs, progression, All-Star...")
        return self

    def finalize(self):
        """Finalisation du dataset joueurs"""
        print("Finalisation du dataset joueurs...")
        initial = len(self.df)
        # Pour ne rien perdre, on remplace NaN par 0 au lieu de dropna
        self.df = self.df.fillna(0)
        print(f"Remplacement des NaN par 0 dans {initial:,} lignes")
        return self

    def save(self):
        """Sauvegarde le dataset final dans output_path"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f"\nFEATURE ENGINEERING JOUEURS TERMINÉ !")
        print(f"Fichier sauvegardé : {self.output_path}")
        print(f"→ {len(self.df):,} stats de joueurs prêtes")
        return self


if __name__ == "__main__":
    PlayersFeatureEngineer(
        "data/cleaned/players/players_clean.csv",
        "data/features/nba_players_features.csv"
    ).load().create_player_features().finalize().save()
