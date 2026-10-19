# main.py

import os

import pandas as pd
from src.scraper.PlayerScraper import PlayerTotalsScraper
from src.scraper.TeamScraper import TeamScraper
from src.scraper.BoxscoreScraper import BoxScoreScraper

# Import des cleaners
from src.cleaning.clean_boxscores import BoxscoreCleaner
from src.cleaning.clean_teams import TeamCleaner
from src.cleaning.clean_players import PlayersCleaner 

from src.features.features_boxscores import BoxscoreFeatureEngineer
from src.features.features_players import PlayersFeatureEngineer  # ← AJOUTÉ
from src.features.features_teams import TeamsFeatureEngineer  # ← AJOUTÉ


# ===========================================
# SCRAPE PLAYERS TOTALS (2010–2024)
# ===========================================
def scrape_players():
    output_dir = os.path.join("data", "raw", "players")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_players_totals_2010_2025.csv")

    if os.path.exists(output_file):
        print("File already exists, skipping players scraping:")
        print(f"→ {output_file}\n")
        return

    all_data_scraper = PlayerTotalsScraper(0)
    all_data_scraper.player_data = []
    all_data_scraper.headers = []

    for year in range(2010, 2025):
        print(f"Scraping player totals for season {year}...")

        scraper = PlayerTotalsScraper(year)

        try:
            scraper.scrape()

            if not all_data_scraper.headers:
                all_data_scraper.headers = scraper.headers

            all_data_scraper.player_data.extend(scraper.player_data)
            print(f"{year}: {len(scraper.player_data)} players extracted.\n")

        except Exception as e:
            print(f"Error for year {year}: {e}")

    all_data_scraper.save_to_csv(output_file)
    print(f"Players data saved → {output_file}\n")


# ===========================================
# SCRAPE TEAMS
# ===========================================
def scrape_teams():
    output_dir = os.path.join("data", "raw", "teams")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_teams.csv")

    if os.path.exists(output_file):
        print("File already exists, skipping team scraping:")
        print(f"→ {output_file}\n")
        return

    try:
        scraper = TeamScraper()
        df = scraper.scrape()
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Teams data saved → {output_file}\n")
    except Exception as e:
        print(f"Error scraping teams: {e}")


# ===========================================
# SCRAPE BOXSCORES (2010–2024)
# ===========================================
def scrape_boxscores():
    output_dir = os.path.join("data", "raw", "boxscores")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_boxscores_2010_2025.csv")

    if os.path.exists(output_file):
        print("File already exists, skipping boxscores scraping:")
        print(f"→ {output_file}\n")
        return

    all_games = []

    for year in range(2010, 2025):
        print(f"\nScraping boxscores for season {year}-{year + 1}...")
        scraper = BoxScoreScraper(year)
        scraper.scrape()
        all_games.extend(scraper.games)

    df = pd.DataFrame(all_games)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"All boxscores saved → {output_file}\n")


# ===========================================
# CLEANING STEP – Boxscores + Teams
# ===========================================
def clean_data():
    print("Starting cleaning phase...\n")

    # --- Clean Boxscores ---
    raw_box = "data/raw/boxscores/nba_boxscores_2010_2025.csv"
    clean_box = "data/cleaned/boxscores/nba_boxscores_clean.csv"

    if os.path.exists(raw_box):
        print("Cleaning boxscores...")
        cleaner_box = BoxscoreCleaner(raw_box, clean_box)
        cleaner_box.load()
        cleaner_box.clean()
        cleaner_box.save()
        print("Boxscores cleaned!\n")
    else:
        print("Raw boxscores not found → skipping\n")

    # --- Clean Teams ---
    raw_teams = "data/raw/teams/nba_teams.csv"
    clean_teams = "data/cleaned/teams/nba_teams_clean.csv"

    if os.path.exists(raw_teams):
        print("Cleaning teams...")
        cleaner_teams = TeamCleaner(raw_teams, clean_teams)
        cleaner_teams.load()
        cleaner_teams.clean()
        cleaner_teams.save()
        print("Teams cleaned!\n")
    else:
        print("Raw teams not found → skipping\n")

    # --- Clean Players ← AJOUTÉ ICI (2 lignes seulement) ---
    raw_players = "data/raw/players/nba_players_totals_2010_2025.csv"
    clean_players = "data/cleaned/players/players_clean.csv"

    if os.path.exists(raw_players):
        print("Cleaning players stats (removing TM rows, fixing decimals...)")
        PlayersCleaner(raw_players, clean_players).run()   # ← C’EST TOUT !
        print("Players cleaned and saved!\n")
    else:
        print("Raw players file not found → skipping\n")

# ===========================================
# FEATURE ENGINEERING STEP – Boxscores + Players + Teams
# ===========================================

def create_features():
    print("Starting feature engineering phase...\n")

    # --- Features Boxscores ---
    input_box = "data/cleaned/boxscores/nba_boxscores_clean.csv"
    output_box = "data/features/nba_boxscores_features.csv"
    if os.path.exists(input_box):
        print("Feature engineering boxscores...")
        BoxscoreFeatureEngineer(input_box, output_box).load().create_team_features().create_game_level_features().finalize().save()
        print("Boxscores features saved!\n")

    # --- Features Players ---
    input_players = "data/cleaned/players/players_clean.csv"
    output_players = "data/features/nba_players_features.csv"
    if os.path.exists(input_players):
        print("Feature engineering players...")
        PlayersFeatureEngineer(input_players, output_players).load().create_player_features().finalize().save()
        print("Players features saved!\n")

    # --- Features Teams ---
    input_teams = "data/cleaned/teams/nba_teams_clean.csv"
    output_teams = "data/features/nba_teams_features.csv"
    if os.path.exists(input_teams):
        print("Feature engineering teams...")
        TeamsFeatureEngineer(input_teams, output_teams).load().create_team_features().finalize().save()
        print("Teams features saved!\n")

# ===========================================
# MAIN PROGRAM
# ===========================================
if __name__ == "__main__":
    import subprocess
    import sys
    from pathlib import Path
    
    print("=" * 50)
    print("     NBA DATA PIPELINE 2010 - 2025")
    print("=" * 50 + "\n")
    
    # ===========================================
    # ÉTAPE 1: SCRAPING
    # ===========================================
    print("📥 ÉTAPE 1/3 : SCRAPING DES DONNÉES")
    print("-" * 50)
    scrape_players()
    scrape_teams()
    scrape_boxscores()
    print("✅ Scraping terminé !\n")
    
    # ===========================================
    # ÉTAPE 2: CLEANING
    # ===========================================
    print("🧹 ÉTAPE 2/3 : NETTOYAGE DES DONNÉES")
    print("-" * 50)
    clean_data()
    print("✅ Nettoyage terminé !\n")
    
    # ===========================================
    # ÉTAPE 3: FEATURE ENGINEERING
    # ===========================================
    print("⚙️  ÉTAPE 3/3 : CRÉATION DES FEATURES")
    print("-" * 50)
    create_features()
    print("✅ Feature engineering terminé !\n")
    
    # ===========================================
    # ÉTAPE 4: LANCEMENT DU DASHBOARD
    # ===========================================
    print("=" * 50)
    print("     LANCEMENT DU DASHBOARD STREAMLIT")
    print("=" * 50 + "\n")
    print("📊 Les données sont prêtes dans data/features/")
    print("🚀 Lancement du dashboard de prédictions...\n")
    
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "src" / "dashboards" / "app.py"
    
    # Run Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])