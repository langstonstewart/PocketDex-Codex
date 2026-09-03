<p align="center">
  <img src="https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/src/images/ui/codex.png" alt="description" width="650"/>
</p>

# PocketDex Codex

![Version](https://img.shields.io/badge/Version-6.1.0-lightgrey) ![License](https://img.shields.io/badge/License-MIT-lightgrey) ![Status](https://img.shields.io/badge/Status-Active-lightgrey)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=flat&logo=qt&logoColor=white)
![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=flat&logo=cloudflare&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white)

**PocketDex Codex**: A full-featured Python-based interactive application for Pokémon Trading Card Game and Pokémon TCG Pocket with a built-in, fully-stocked Pokédex. It tracks every card across the game's entire print history, every Pokémon across every region, and syncs new sets and artwork automatically over the network.

*This tool is currently only available for Windows. An internet connection is required to fetch card images.*

![PocketDex Codex Grid](https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/src/images/ui/codex_grid.png)

## Highlights

- **Over 170 Sets and Counting** — The complete TCG catalog from the WotC era to Mega Evolution plus every TCG Pocket expansion.
- **Live Collection Tracking** — Card quantity counters, bulk add/remove, favoriting, and completion percentages calculated per set, per series, and nationally.
- **Complete National Pokédex** — All 1025 Pokémon with typing, gender ratios, height/weight, Pokédex entries, regional/alternate forms, and Gigantamax/Dynamax forms, browsable by region with instant search.
- **Card ⇄ Dex Link** — Jump straight from a card in your binder to its matching Pokédex entry.
- **Auto-Updating Set & Pokédex Data** — Set lists and Pokédex data are pulled live from the repository, so new sets and corrections roll out without needing a new release.
- **Cloudflare-Backed Asset Pipeline** — Pokédex sprites are served from an R2 bucket directly into the app to cache.
- **Import/Export** — Collections can be exported to and imported from Excel (`.xlsx`) for backup or sharing, alongside local JSON.
- **Polished UI** — Light/dark theming, animated icon/image fade-ins, adjustable grid column counts, and live countdown timers for unreleased sets.

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop application | Python 3, [PyQt6](https://pypi.org/project/PyQt6) (Widgets, Multimedia, Network) |
| Data fetching / parsing | `requests`, `beautifulsoup4`, `pandas` (Excel import/export), `concurrent.futures` for parallel image/data fetches |
| Collection & Pokédex data | JSON, versioned and distributed from the repo (`set_data_git/`) |
| Asset delivery | Cloudflare Pages + Pages Functions (`functions/[[catchall]].js`) fronting an R2 bucket, with `Cache-Control` edge caching for images |
| Companion site | Static HTML landing page hosted on Cloudflare Pages |


## How To Use (Installation)

#### 1. Install the project folder:
Installing Python is not needed; simply download the latest ZIP folder via current release and launch the executable within:
https://github.com/langstonstewart/PocketDex-Codex/releases

#### 2. (Optional) Download Pokémon Trading Card Game Pocket:
[![Download on the App Store](https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Download_on_the_App_Store_RGB_blk.svg/330px-Download_on_the_App_Store_RGB_blk.svg.png)](https://apps.apple.com/app/id6479970832) [![Get it on Google Play](https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Google_Play_Store_badge_EN.svg/330px-Google_Play_Store_badge_EN.svg.png)](https://play.google.com/store/apps/details?id=jp.pokemon.pokemontcgp)

## Contact:

If you encounter any issues or have questions, feel free to contact the maintainer at langston.professional08@gmail.com or open an issue on the GitHub repository.

## License:

This project is licensed under the MIT License – see the LICENSE file for details.
