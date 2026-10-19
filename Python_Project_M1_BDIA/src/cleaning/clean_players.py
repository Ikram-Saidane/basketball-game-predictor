import os
import pandas as pd
import re

class PlayersCleaner:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None

    def load_data(self):
        """Load CSV file into a DataFrame."""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.df = pd.read_csv(self.input_path)
        print(f" Data loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")

    def convert_decimal_format(self):
        """
        Convert values like '.446' to '0.446'.
        Applies only to columns with string values.
        """
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].map(
                lambda val: "0" + val if isinstance(val, str) and re.match(r"^\.\d+$", val) else val
            )
        print(" Decimal conversion (.xxx → 0.xxx) completed.")

    def remove_TM_rows(self):
        """Remove rows where Team contains 'TM' (TM, 2TM, 3TM, etc.)."""
        # Nettoyer les espaces dans les noms de colonnes
        self.df.columns = self.df.columns.str.strip()

        if "Team" not in self.df.columns:
            raise KeyError(f"Column 'Team' not found in dataset! Columns: {self.df.columns.tolist()}")

        before = self.df.shape[0]
        # Supprimer toutes les lignes où Team contient "TM"
        self.df = self.df[~self.df["Team"].str.contains("TM", na=False)]
        after = self.df.shape[0]

        print(f"Removed {before - after} rows where Team contained 'TM'")

    def save_clean_data(self):
        """Save cleaned data to CSV."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f" Clean data saved to: {self.output_path}")

    def run(self):
        """Execute all steps."""
        self.load_data()
        self.convert_decimal_format()
        self.remove_TM_rows()
        self.save_clean_data()
        print(" Cleaning process finished.")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier du script
    INPUT_FILE = os.path.join(BASE_DIR, "../../data/raw/players/nba_players_totals_2010_2025.csv")
    OUTPUT_FILE = os.path.join(BASE_DIR, "../../data/cleaned/players/players_clean.csv")

    cleaner = PlayersCleaner(INPUT_FILE, OUTPUT_FILE)
    cleaner.run()
