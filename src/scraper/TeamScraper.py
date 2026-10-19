import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd


class TeamScraper:
    def __init__(self):
        self.url = "https://www.basketball-reference.com/teams/"
        self.scraper = cloudscraper.create_scraper()  # bypass 403 problem w 5aliwha haka w amen ma tmeshech
        self.headers = []

    def scrape(self):
        print(f"Scraping teams from {self.url} ...")

        response = self.scraper.get(self.url)
        if response.status_code != 200:
            raise ValueError(f"HTTP Error {response.status_code} (Forbidden)")

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "teams_active"})
        if not table:
            raise ValueError("Could not find table 'teams_active'")

        # Extract headers
        raw_headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        if not raw_headers:
            raw_headers = ["Franchise", "Lg", "From", "To", "Yrs", "G", "W", "L",
                           "W/L%", "Plyfs", "Div", "Conf", "Champ"]

        # Extract rows
        rows = []
        for row in table.find("tbody").find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
            if cols:
                rows.append(cols)

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=raw_headers)
        return df
