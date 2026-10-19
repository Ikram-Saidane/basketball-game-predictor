
import os
import pandas as pd

class BoxscoreCleaner:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Fichier introuvable : {self.input_path}")

        self.df = pd.read_csv(self.input_path)
        print(f"Chargement de {len(self.df):,} matchs bruts depuis {self.input_path}")

    def clean(self):
        if self.df is None:
            raise ValueError("Aucun DataFrame chargé – lance .load() d'abord")

        df = self.df.copy()

        # 1. Forcer les noms de colonnes attendus
        expected = ["Date", "AwayTeam", "HomeTeam", "AwayPts", "HomePts"]
        if list(df.columns) != expected:
            print("Renommage des colonnes pour correspondre au standard")
            df.columns = expected

        # 2. Nettoyer les noms d'équipes
        df["AwayTeam"] = df["AwayTeam"].astype(str).str.strip()
        df["HomeTeam"] = df["HomeTeam"].astype(str).str.strip()

        # 3. Convertir les scores en entiers
        df["AwayPts"] = pd.to_numeric(df["AwayPts"], errors="coerce").fillna(0).astype(int)
        df["HomePts"] = pd.to_numeric(df["HomePts"], errors="coerce").fillna(0).astype(int)

        # 4. CONVERSION DATE – c'est la partie que tu voulais
        print("Conversion des dates (ex: 'Tue, Oct 26, 2010' → '26/10/2010')...")
        # Parse le format exact avec le jour de la semaine + virgule
        df["Date"] = pd.to_datetime(df["Date"], format="%a, %b %d, %Y", errors="coerce")

        # Gestion des dates invalides (très rare ici mais par sécurité)
        nb_invalid = df["Date"].isna().sum()
        if nb_invalid > 0:
            print(f"{nb_invalid} dates invalides détectées → supprimées")
            df = df.dropna(subset=["Date"])

        # Format final DD/MM/YYYY
        df["Date"] = df["Date"].dt.strftime("%d/%m/%Y")

        # 5. Colonnes utiles supplémentaires
        df["PointDiff"] = df["HomePts"] - df["AwayPts"]
        df["Winner"] = df.apply(
            lambda row: row["HomeTeam"] if row["HomePts"] > row["AwayPts"] else row["AwayTeam"],
            axis=1
        )

        # 6. Nettoyage final
        initial = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        print(f"Nettoyage terminé → {initial - len(df)} doublons supprimés")

        self.df = df
        print(f"Prêt ! {len(self.df):,} matchs nettoyés avec dates au format JJ/MM/AAAA")

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False, encoding="utf-8")
        print(f"Fichier propre sauvegardé ici : {self.output_path}")


# ========================================
# Lancement direct du script
# ========================================
if __name__ == "__main__":
    RAW_FILE = "data/raw/boxscores/nba_boxscores_2010_2025.csv"
    CLEAN_FILE = "data/cleaned/boxscores/nba_boxscores_clean.csv"

    cleaner = BoxscoreCleaner(RAW_FILE, CLEAN_FILE)
    cleaner.load()
    cleaner.clean()
    cleaner.save()

    print("\nTout est bon, ton fichier est prêt pour les modèles IA !")