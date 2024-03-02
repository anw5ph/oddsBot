# OddsBot README

## Introduction
OddsBot is a Discord bot designed to fetch and display betting odds for various sports leagues. Utilizing The Odds API, it offers users the ability to query current odds for their favorite leagues directly within Discord, providing a convenient and quick way to access this information.

## Features
* Fetch current betting odds for specified sports leagues.
* Display odds in a user-friendly format directly within Discord.
* Support for multiple bookmakers, showcasing a range of betting options.
* Customizable command prefix and role-based command access.

## Setup Instructions
### Prerequisites
* Python 3.8 or higher
* Discord account and a Discord server
* An API key from The Odds API

### Installation
1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
3. Create a `.env` file in the root directory of the project and add the following variables:
``` {makefile}
DISCORD_TOKEN=<Your_Discord_Bot_Token>
DISCORD_GUILD=<Your_Discord_Guild_ID>
ODDS_API_KEY=<Your_The_Odds_API_Key>
```
4. Replace the placeholders with your actual Discord token, guild ID, and The Odds API key.

*** Running the Bot
Execute the bot by running `python bot.py` in your terminal. Ensure you're in the project's root directory.

** Usage
* **Fetching Odds:** Use the `!get-odds <league>` command to fetch current odds for the specified league. You must have the 'Admin' role to use this command.
* **Viewing Help:** Use `!help` to view all available commands and their descriptions.

** Contributing
Contributions to OddsBot are welcome! If you have suggestions for improvements or new features, please feel free to create an issue or open a pull request.

*** Guidelines
* Fork the repository and create your branch from `main`.
* If you've added code that should be tested, add tests.
* Ensure your code lints and follows the existing code style.
* Update the `README.md` with details of changes, including new environment variables, exposed ports, useful file locations, and container parameters.
* Issue your pull request with a comprehensive description of changes.

** License
[Your License Here] - Typically, open-source projects are released under licenses such as MIT, GPL, etc. Ensure to include your chosen license text in a LICENSE file in the root of the project.
