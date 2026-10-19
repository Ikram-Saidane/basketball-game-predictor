import os
from src.scraper.PlayerScraper import PlayerTotalsScraper
from src.scraper.TeamScraper import TeamScraper
from src.scraper.BoxscoreScraper import BoxScoreScraper
import pandas as pd

# ===========================================
# SCRAPE PLAYERS TOTALS (2010–2024)
# ===========================================
def scrape_players():
    output_dir = os.path.join("data", "raw", "players")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_players_totals_2010_2025.csv")

    if os.path.exists(output_file):
        print("⚠️ File already exists, skipping players scraping:")
        print(f"→ {output_file}\n")
        return

    all_data_scraper = PlayerTotalsScraper(0)
    all_data_scraper.player_data = []
    all_data_scraper.headers = []

    for year in range(2010, 2025):
        print(f"Scraping totals for season {year}...")
        scraper = PlayerTotalsScraper(year)
        try:
            scraper.scrape()
            if not all_data_scraper.headers:
                all_data_scraper.headers = scraper.headers
            all_data_scraper.player_data.extend(scraper.player_data)
            print(f"{year}: {len(scraper.player_data)} players extracted.\n")
        except Exception as e:
            print(f"❌ Error for year {year}: {e}")

    all_data_scraper.save_to_csv(output_file)
    print(f"✅ Players data saved to {output_file}\n")


# ===========================================
# SCRAPE TEAMS
# ===========================================
def scrape_teams():
    output_dir = os.path.join("data", "raw", "teams")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_teams.csv")

    if os.path.exists(output_file):
        print("⚠️ File already exists, skipping team scraping:")
        print(f"→ {output_file}\n")
        return

    try:
        scraper = TeamScraper()
        df = scraper.scrape()
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"✅ Teams data saved to {output_file}")
    except Exception as e:
        print(f"❌ Error scraping teams: {e}")


# ===========================================
# SCRAPE BOXSCORES (2010–2024)
# ===========================================
def scrape_boxscores():
    output_dir = os.path.join("data", "raw", "boxscores")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "nba_boxscores_2010_2025.csv")

    if os.path.exists(output_file):
        print("⚠️ File already exists, skipping boxscores scraping:")
        print(f"→ {output_file}\n")
        return

    all_games = []
    for year in range(2010, 2025):
        print(f"\nScraping boxscores for season {year}-{year+1}...")
        scraper = BoxScoreScraper(year)
        scraper.scrape()
        all_games.extend(scraper.games)

    df = pd.DataFrame(all_games)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ All boxscore data saved to {output_file}")


# ===========================================
# MAIN PROGRAM
# ===========================================
if __name__ == "__main__":
    scrape_players()
    scrape_teams()
    scrape_boxscores()
