
# Recipe Scraper for Diabetes Food Hub

This repository hosts the development of a web scraping project that extracts recipes from [Diabetes Food Hub](https://diabetesfoodhub.org/). The project is designed to collect detailed recipe data and provide it in both Spanish and English.

## Project Structure

- **/recipes**: Contains the scraped recipe data in Spanish, saved in JSON format.
- **/translations/all_recipes_EN**: Holds the same recipes translated into English.
- **/scripts**: Includes the main scraping scripts and utility functions.
  - **scraping**: Contains specific scripts for extracting recipe URLs and details.
  - **utils**: Includes helper functions to support the scraping process.
- **/logs/fail**: Stores log files for any failed scraping attempts, helping to identify and resolve issues.

## How to Use

1. Run the scripts in `/scripts/scraping` to scrape recipe data.
2. The resulting recipes will be stored in `/recipes` in Spanish.
3. To access translated recipes in English, refer to `/translations/all_recipes_EN`.

## Repository Contents

- **config/**: Configuration files.
- **data/**: Additional data resources used in scraping and analysis.
- **translations/**: Folder containing scripts and files for recipe translation.
- **count_files**: Text files to track categories, ingredients, and tags extracted from the recipes.

## Requirements

- Python 3.x
- Required libraries: BeautifulSoup, requests, and others listed in `requirements.txt`.
