import requests
from collections import defaultdict
import os
from dotenv import load_dotenv
import json

import discord
from discord import app_commands
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()

    except Exception as e:
        print(e)

def getOdds(leagueName, market, eventId = None, prop = None):
    if market == 'h2h' or market == 'spreads' or market == 'totals':
        response = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{leagueName}/odds/",
            params={
                "regions": "us",
                "markets": market,
                "oddsFormat": "american",
                "apiKey": ODDS_API_KEY
            })
    elif market == 'player_props':
        response = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{leagueName}/events/{eventId}/odds?",
            params={
                "regions": "us",
                "markets": prop,
                "oddsFormat": "american",
                "apiKey": ODDS_API_KEY
            })

    messages = []
    if market == 'h2h':
        for event in response.json():
            header = f"{event['away_team']} at {event['home_team']} (Start Time: {event['commence_time'].replace('T', ' ').replace('Z', '')})"
            messages.append(header)
            messages.append("-" * 35)

            outcomes = defaultdict(list)

            for bookmaker in event['bookmakers']:
                bookmaker_info = f"**{bookmaker['title']} (Last Updated: {bookmaker['last_update'].replace('T', ' ').replace('Z', '')})**"
                messages.append(bookmaker_info)

                for market in bookmaker['markets']:
                    for outcome in market['outcomes']:
                        sign = '+' if outcome['price'] > 0 else ''
                        outcome_info = f"{outcome['name']}: {sign}{outcome['price']}"
                        outcomes[bookmaker['title']].append(outcome_info)

                for outcome_info in outcomes[bookmaker['title']]:
                    messages.append(outcome_info)

                messages.append("-" * 35)

            messages.append("=" * 100)
    elif market == 'spreads' or market == 'totals':
         for event in response.json():
            header = f"{event['away_team']} at {event['home_team']} (Start Time: {event['commence_time'].replace('T', ' ').replace('Z', '')})"
            messages.append(header)
            messages.append("-" * 35)

            outcomes = defaultdict(list)

            for bookmaker in event['bookmakers']:
                bookmaker_info = f"**{bookmaker['title']} (Last Updated: {bookmaker['last_update'].replace('T', ' ').replace('Z', '')})**"
                messages.append(bookmaker_info)

                for market in bookmaker['markets']:
                    for outcome in market['outcomes']:
                        priceSign = '+' if outcome['price'] > 0 else ''
                        pointSign = '+' if outcome['point'] > 0 else ''
                        outcome_info = f"{outcome['name']}: {pointSign}{outcome['point']} ({priceSign}{outcome['price']})"
                        outcomes[bookmaker['title']].append(outcome_info)

                for outcome_info in outcomes[bookmaker['title']]:
                    messages.append(outcome_info)

                messages.append("-" * 35)

            messages.append("=" * 100)
    elif market == 'player_props':
        data = response.json()

        header = f"{data['home_team']} vs {data['away_team']} (Start Time: {data['commence_time'].replace('T', ' ').replace('Z', '')})"
        print(header)
        messages.append(header)
        messages.append("-" * 35)

        outcomes = defaultdict(list)

        for bookmaker in data['bookmakers']:
            bookmaker_info = f"**{bookmaker['title']}"
            messages.append(bookmaker_info)

            for market in bookmaker['markets']:
                messages[-1] = f"{messages[-1]} (Last Updated: {market['last_update'].replace('T', ' ').replace('Z', '')})**"

                for outcome in market['outcomes']:
                    priceSign = '+' if outcome['price'] > 0 else ''
                    pointSign = '+' if outcome['point'] > 0 else ''
                    outcome_info = f"{outcome['description']}: {outcome['name']} {pointSign}{outcome['point']} ({priceSign}{outcome['price']})"
                    outcomes[bookmaker['title']].append(outcome_info)

            for outcome_info in outcomes[bookmaker['title']]:
                messages.append(outcome_info)

            messages.append("-" * 35)

        messages.append("=" * 100)


    return messages

def split_text_for_embed(text, split_length=1024):
    return [text[i:i+split_length] for i in range(0, len(text), split_length)]

async def send_embeds_in_chunks(interaction: discord.Interaction, embeds):
    for embed in embeds:
        embed.set_footer(text=f"Odds are subject to change.")
        await interaction.followup.send(embed=embed)

@bot.tree.command(name='get-team-odds', description='Get the current odds for a specific team in a specific league')
@commands.has_role('Admin')
@app_commands.describe(league = "What league do you want me to get odds for?", market = "What type of odds do you want me to get?")
@app_commands.choices(league = [app_commands.Choice(name = 'NBA', value = 'basketball_nba')], 
                      market = [app_commands.Choice(name = 'Spreads', value = 'spreads'), app_commands.Choice(name = 'Totals', value = 'totals'), app_commands.Choice(name = 'H2H', value = 'h2h')])
async def odds(interaction: discord.Interaction, league: app_commands.Choice[str], market: app_commands.Choice[str]):

    oddsList = getOdds(league.value, market.value)

    if len(oddsList) == 0:
        embed = discord.Embed(title=f"No events found for the `{league.name}`", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    
    embeds = []
    embed = discord.Embed(title=f"Current Odds for {league.name} - {market.name}", color=0x00ff00)
    embed.set_footer(text=f"Odds are subject to change.")
    embeds.append(embed)

    i = 0
    for j in range(len(oddsList)):
        if oddsList[j] == "=" * 100:
            event_title = oddsList[i]
            odds_section = '\n'.join(oddsList[i+1:j])
            split_odds_sections = split_text_for_embed(odds_section)

            for index, section in enumerate(split_odds_sections):
                part_title = f"**{event_title}**" if index == 0 else f"**{event_title} (Part {index + 1})**"
                # Check if adding this field exceeds the field limit or size limit
                if len(embed.fields) >= 25 or len(embed) + len(part_title) + len(section) > 6000:
                    embed = discord.Embed(color=0x00ff00)
                    embeds.append(embed)

                if index == 0 and len(split_odds_sections) > 1:
                    part_title = f"**{event_title} (Part {index + 1})**"
                elif index == 0:
                    part_title = f"**{event_title}**"
                else:
                    part_title = f"**{event_title} (Part {index + 1})**"
                embed.add_field(name=part_title, value=section, inline=False)

            i = j + 1

    # Respond with the first embed and follow up with any additional embeds
    await interaction.response.send_message(embed=embeds[0])
    if len(embeds) > 1:
        await send_embeds_in_chunks(interaction, embeds[1:])

    await interaction.response.send_message(embed=embed)

def get_props(league):
    if league == 'basketball_nba':
        return [
            ("Points (Over/Under)", "player_points"),
            ("Rebounds (Over/Under)", "player_rebounds"),
            ("Assists (Over/Under)", "player_assists"),
            ("Threes (Over/Under)", "player_threes"),
            ("Blocks (Over/Under)", "player_blocks"),
            ("Steals (Over/Under)", "player_steals"),
            ("Blocks + Steals (Over/Under)", "player_blocks_steals"),
            ("Turnovers (Over/Under)", "player_turnovers"),
            ("Points + Rebounds + Assists (Over/Under)", "player_points_rebounds_assists"),
            ("Points + Rebounds (Over/Under)", "player_points_rebounds"),
            ("Points + Assists (Over/Under)", "player_points_assists"),
            ("Rebounds + Assists (Over/Under)", "player_rebounds_assists"),
            ("First Basket Scorer (Yes/No)", "player_first_basket"),
            ("Double Double (Yes/No)", "player_double_double"),
            ("Triple Double (Yes/No)", "player_triple_double")]
    
def get_upcoming_games():
    with open('upcomingGames.json') as f:  
        data = json.load(f)
    return data

@bot.tree.command(name='get-props', description='Get the current player props for a specific team in a specific league')
@commands.has_role('Admin')
@app_commands.describe(event = "What game do you want me to get props for?", prop = "What type of props do you want me to get?")
@app_commands.choices(event = [app_commands.Choice(name = gameTeams, value = gameId) for gameId, gameTeams in get_upcoming_games().items()], 
                      prop = [app_commands.Choice(name = prop[0], value = prop[1]) for prop in get_props('basketball_nba')])
async def propOdds(interaction: discord.Interaction, event: app_commands.Choice[str], prop: app_commands.Choice[str]):
    
    oddsList = getOdds("basketball_nba", "player_props", event.value, prop.value)

    if len(oddsList) == 0:
        embed = discord.Embed(title=f"No events found for `{event.name}`", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    
    embeds = []
    embed = discord.Embed(title=f"Current Odds for {event.name} - {prop.name}", color=0x00ff00)
    embed.set_footer(text=f"Odds are subject to change.")
    embeds.append(embed)

    i = 0
    for j in range(len(oddsList)):
        if oddsList[j] == "=" * 100:
            event_title = oddsList[i]
            odds_section = '\n'.join(oddsList[i+1:j])
            split_odds_sections = split_text_for_embed(odds_section)

            for index, section in enumerate(split_odds_sections):
                part_title = f"**{event_title}**" if index == 0 else f"**{event_title} (Part {index + 1})**"
                # Check if adding this field exceeds the field limit or size limit
                if len(embed.fields) >= 25 or len(embed) + len(part_title) + len(section) > 6000:
                    embed = discord.Embed(color=0x00ff00)
                    embeds.append(embed)

                if index == 0 and len(split_odds_sections) > 1:
                    part_title = f"**{event_title} (Part {index + 1})**"
                elif index == 0:
                    part_title = f"**{event_title}**"
                else:
                    part_title = f"**{event_title} (Part {index + 1})**"
                embed.add_field(name=part_title, value=section, inline=False)

            i = j + 1

    # Respond with the first embed and follow up with any additional embeds
    await interaction.response.send_message(embed=embeds[0])
    if len(embeds) > 1:
        await send_embeds_in_chunks(interaction, embeds[1:])

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
