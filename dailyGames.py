import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
response = requests.get("https://api.the-odds-api.com/v4/sports/basketball_nba/events", params={"apiKey": ODDS_API_KEY})
data = response.json()

upcomingGames = {}
for game in data:
    if game['id'] not in upcomingGames:
        upcomingGames[game['id']] = game['home_team'] + " vs " + game['away_team']

with open('upcomingGames.json', 'w') as f:
    json.dump(upcomingGames, f, indent = 4)
