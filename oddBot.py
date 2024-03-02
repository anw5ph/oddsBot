import requests
from collections import defaultdict
import os
from dotenv import load_dotenv

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
        sync = await bot.tree.sync()

    except Exception as e:
        print(e)
        
def getOdds(leagueName):
    response = requests.get(
        "https://api.the-odds-api.com/v4/sports/upcoming/odds/",
        params={
            "regions": "us",
            "markets": "h2h",
            "oddsFormat": "american",
            "apiKey": ODDS_API_KEY
        })
    events = [event for event in response.json() if event["sport_title"] == leagueName]

    messages = []
    for event in events:
        header = f"{event['away_team']} at {event['home_team']} (Start Time: {event['commence_time'].replace('T', ' ').replace('Z', '')})"
        messages.append(header)
        messages.append("-" * 50)

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

            messages.append("-" * 50)

        messages.append("=" * 100)

    return messages

def split_text_for_embed(text, split_length=1024):
    """
    Splits a long text into chunks of `split_length` characters each.
    """
    return [text[i:i+split_length] for i in range(0, len(text), split_length)]

@bot.tree.command(name='get-odds')
@commands.has_role('Admin')
@app_commands.describe(league = "What league do you want me to get odds for?")
async def odds(interaction: discord.Interaction, league: str):

    i = 0
    oddsList = getOdds(league)
    if len(oddsList) == 0:
        embed = discord.Embed(title=f"No events found for the `{league}`", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(title=f"Current Odds for {league}", color=0x00ff00)
    embed.set_footer(text=f"Odds are subject to change.")

    i = 0
    for j in range(len(oddsList)):
        if oddsList[j] == "=" * 100:
            event_title = oddsList[i]

            odds_section = '\n'.join(oddsList[i+1:j])

            split_odds_sections = split_text_for_embed(odds_section)

            for index, section in enumerate(split_odds_sections):
                if index == 0 and len(split_odds_sections) > 1:
                    part_title = f"**{event_title} (Part {index + 1})**"
                elif index == 0:
                    part_title = f"**{event_title}**"
                else:
                    part_title = f"**{event_title} (Part {index + 1})**"
                embed.add_field(name=part_title, value=section, inline=False)

            i = j + 1

    if i < len(oddsList):
        odds_section = '\n'.join(oddsList[i:])
        event_title = oddsList[i].split(":")[0]
        split_odds_sections = split_text_for_embed(odds_section)

        for index, section in enumerate(split_odds_sections):
            part_title = f"{event_title}" if len(split_odds_sections) == 1 else f"{event_title} (Part {index + 1})"
            embed.add_field(name=part_title, value=section, inline=False)

    if len(embed.fields) > 25:
        embed = discord.Embed(title="Error", description="Too many events to display in one message. Please narrow your search.", color=0xff0000)

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
