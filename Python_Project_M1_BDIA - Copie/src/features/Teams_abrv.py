# src/features/teams_abrv.py

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


def get_abbreviation(team_name: str):
    """Retourne l'abréviation d'une franchise (ou None si inconnue)."""
    return ABBREVIATIONS.get(team_name)


def map_abbreviations(df, col="Franchise_clean"):
    """Ajoute une colonne Abbreviation au dataframe sans toucher aux fichiers."""
    df["Abbreviation"] = df[col].map(ABBREVIATIONS)
    return df
