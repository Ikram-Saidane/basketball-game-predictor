import csv
import cloudscraper
from bs4 import BeautifulSoup

class PlayerTotalsScraper:
    def __init__(self, year):
        self.year = year
        self.url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
        self.scraper = cloudscraper.create_scraper()  
        self.headers = []
        self.player_data = []

    def scrape(self):
        response = self.scraper.get(self.url)

        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code} for year {self.year}")

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "totals_stats"})

        if not table:
            raise ValueError(f"Table not found for year {self.year}")

        # Extract headers once
        if not self.headers:
            self.headers = [th.text.strip() for th in table.find("thead").find_all("th")][1:]

        # Extract rows
        rows = table.find("tbody").find_all("tr")

        for row in rows:
            if "class" in row.attrs and "thead" in row.attrs["class"]:
                continue
            cols = row.find_all("td")
            if cols:
                self.player_data.append([col.text.strip() for col in cols])

    def save_to_csv(self, filepath):
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            writer.writerows(self.player_data)
