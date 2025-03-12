# PocketDex Codex
![Version](https://img.shields.io/badge/Version-1.0.0-lightgrey)  ![Python](https://img.shields.io/badge/Python-3.10%2B-lightgrey) ![License](https://img.shields.io/badge/License-MIT-lightgrey) ![Status](https://img.shields.io/badge/Status-Active-lightgrey)

A python-based interactive CLI tool for Pokémon Trading Card Game Pocket.

- Manage your collection
- Save and load your collection in CSV/JSON format
- Create decks for battling
- Track your completion throughout different sets, and much more!

### All Current Implemented Sets:
---
| **Set Name:**                         | **Release Date:**                    |
|:------------------------------------:|:------------------------------------:
| **Genetic Apex (A1)**                | **October 30th, 2024**              |
| **Promo-A (P-A)**                    | **October 30, 2024**                |
| **Mythical Island (A1a)**            | **December 17th, 2024**             |
| **Space-Time Smackdown (A2)**        | **January 29th, 2025**              |
| **Triumphant Light (A2a)**           | **February 28th, 2025**             |

### Sets TBA:
---
| **Set Name**                         | **Release Date**                    |
|:------------------------------------:|:------------------------------------:
| **??? (A3)**                | **April 30th, 2025**              |

*This tool is currently only available for Windows.*

## How To Use (Installation):

#### 1. Download Pokémon Trading Card Game Pocket:
[![Download on the App Store](https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/images/app-store-badge-en.webp)](https://apps.apple.com/app/id6479970832) [![Get it on Google Play](https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg)](https://play.google.com/store/apps/details?id=jp.pokemon.pokemontcgp)


#### 2. Install Python:
 In your preferred terminal, paste in the following code:

````
winget install Python
````
or install the latest version from:
https://www.python.org/downloads/

#### 3. Install the project folder:
Download the project folder via current release:
https://github.com/langstonstewart/PocketDex-Codex/releases

## Basic Usage:

Once you’ve installed everything, you can run the tool by navigating to the project folder and running the BATCH file.
This should start the interactive CLI tool. 
Enter a username, and start managing your collection!

## Adding Entries:
In the app, you'll find the cards set number under the card description. 
Use these set numbers to add cards to your collection!

![card_img](https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/images/card_img.png)

Your entries will be sorted and saved within a CSV file, ready to be called upon and/or written at any time.
Accidental entries can be deleted as well.
## Creating Decks:
To create a deck, follow all user input questions accordingly:
- Deck Name
- Highlight Card of Deck
- Best Matchup(s)
- Worst Matchup(s)
- Energy Usage
- Description of Deck
- Personal Deck Ranking
- End Statement of Deck

Use card set numbers to add cards to the deck, with an optional description on how to use that specific card.
![deck_img](https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/images/deck_img.png)

No need for entries. Cards can be added to a deck regardless of entry status.
Once completed, the deck will be saved as a JSON file, ready to be viewed within the CLI tool.
## Contact:

If you encounter any issues or have questions, feel free to contact the maintainer at langston.professional08@gmail.com or open an issue on the GitHub repository.

## License:

This project is licensed under the MIT License – see the LICENSE file for details.



