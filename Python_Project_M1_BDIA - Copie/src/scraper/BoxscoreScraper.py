import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

class BoxScoreScraper:
    """
    Scrapes NBA game results (date, teams, score) for a given season.
    """
    def __init__(self, season_year):
        """
        season_year: starting year of the NBA season, e.g. 2023 for 2023-2024
        """
        self.season_year = season_year
        self.scraper = cloudscraper.create_scraper()
        self.games = []
        self.months = [
            "october", "november", "december",
            "january", "february", "march", "april" , "may" , "june"
        ]

    def scrape(self):
        end_year = self.season_year + 1

        for month in self.months:
            url = f"https://www.basketball-reference.com/leagues/NBA_{end_year}_games-{month}.html"
            print(f"Scraping {month.capitalize()} games for {self.season_year}-{end_year} season from {url}...")

            try:
                response = self.scraper.get(url)
                if response.status_code != 200:
                    print(f" Failed to fetch {url}, status code: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", id="schedule")
                if not table:
                    print(f" Schedule table not found for {month} {self.season_year}-{end_year}")
                    continue

                rows = table.find("tbody").find_all("tr")
                for row in rows:
                    if row.get("class") and "thead" in row.get("class"):
                        continue  

                    date = row.find("th", {"data-stat": "date_game"}).text.strip()
                    away = row.find("td", {"data-stat": "visitor_team_name"}).text.strip()
                    home = row.find("td", {"data-stat": "home_team_name"}).text.strip()
                    away_pts = row.find("td", {"data-stat": "visitor_pts"})
                    home_pts = row.find("td", {"data-stat": "home_pts"})

                    away_pts = away_pts.text.strip() if away_pts else ""
                    home_pts = home_pts.text.strip() if home_pts else ""

                    self.games.append({
                        "Date": date,
                        "AwayTeam": away,
                        "HomeTeam": home,
                        "AwayPts": away_pts,
                        "HomePts": home_pts
                    })

            except Exception as e:
                print(f" Error scraping {month} {self.season_year}-{end_year}: {e}")

        print(f" Total games scraped for {self.season_year}-{end_year}: {len(self.games)}")

    def save_to_csv(self, filepath):
        df = pd.DataFrame(self.games)
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f" Boxscore data saved to {filepath}")


# Example usage
scraper = BoxScoreScraper(2023)
scraper.scrape()
scraper.save_to_csv("nba_2023_2024_games.csv")
