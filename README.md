# Ispirami - Recipe Recommendation System

A smart recipe recommendation system that scrapes recipes from Giallo Zafferano and matches them with ingredients available in your fridge.

## Features

- **Automatic recipe scraping** from Giallo Zafferano
- **Configurable scraping scope** - control how many pages to scrape (1 page, N pages, or all available pages)
- **Structured recipe storage** - each recipe saved as JSON with title, ingredients, features, nutritional values, and recipe link
- **Smart ingredient matching** based on your available ingredients
- **Conditional execution** - only scrapes when needed
- **Easy-to-use pipeline** with automatic dependency management
- **Rate limiting** - built-in delays to be respectful to the website (1s between recipes, 10s between pages)

## Project Structure

```
ispirami/
├── main.py                 # Main pipeline orchestrator
├── matcher.py              # Recipe matching logic
├── scraper.py              # Recipe scraping from Giallo Zafferano
├── NLP_alberto.py          # NLP processing using Alberto model
├── model_recipe.py         # Recipe data model
├── quantity_udm_parser.py  # Quantity and unit parsing
├── run_pipeline.sh         # Automated execution script
├── requirements.txt        # Python dependencies
├── fridge.json            # Your available ingredients
└── recipes/               # Downloaded recipe database
    ├── spaghetti_alla_carbonara.json
    ├── crepes_dolci_e_salate.json
    └── ...
```

## Quick Start

### Option 1: Automated Pipeline (Recommended)
```bash
./run_pipeline.sh
```

This script will:
1. Install required dependencies automatically
2. Run the scraper only if the Recipes folder doesn't exist
3. Execute the matcher to find recipes you can make
4. Display results clearly

### Option 2: Manual Execution
```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run the pipeline
python3 main.py
```

## How It Works

1. **Conditional Scraping**: The system checks if the `recipes/` folder exists
   - If it doesn't exist: Runs the scraper to download recipes from Giallo Zafferano
   - If it exists: Skips scraping and uses existing recipes

2. **Ingredient Matching**: The matcher compares your available ingredients (from `fridge.json`) with recipe ingredients using smart matching logic

3. **Results**: Shows either:
   - "No recipes found" if no matches are available
   - A list of recipe URLs you can make with your ingredients

## Configuration

### Setting Your Available Ingredients

Edit `fridge.json` to include the ingredients you have:

```json
{
  "olio": "1 l",
  "sale fino": "1 kg", 
  "pasta": "1 kg",
  "uova": "10",
  "farina 00": "1 kg",
  "zucchero": "1 kg",
  "burro": "1 kg"
}
```

## Dependencies

- `bs4` - Beautiful Soup for web scraping
- `requests` - HTTP library for web requests

## Recipe Data Structure

Each recipe is saved as a JSON file in the `recipes/` folder with the following structure:

```json
{
  "title": "Recipe Title",
  "ingredients": [
    "Ingredient 1: quantity",
    "Ingredient 2: quantity"
  ],
  "features": {
    "Difficoltà": "Easy",
    "Preparazione": "15 min",
    "Cottura": "30 min",
    "Porzioni": "4"
  },
  "nutritional_values": {
    "Calorie": 350.0,
    "Proteine": 15.2,
    "Carboidrati": 45.8,
    "Grassi": 12.3
  },
  "recipe_link": "https://ricette.giallozafferano.it/recipe-url.html"
}
```

## NLP Module

The `NLP_alberto.py` module provides natural language processing capabilities for ingredient analysis:

- **Tokenization**: Breaks down ingredient strings into individual tokens
- **POS Analysis**: Basic part-of-speech tagging for ingredients
- **Dependency Analysis**: Basic dependency parsing for ingredient structure
- **Integration Ready**: Designed to be connected with the scraper for automated ingredient processing

The module expects ingredients in the format "ingredient_name: quantity" and returns structured tokenization results.

## Output Example

```
Starting ispirami pipeline...
Requirements installed successfully.
Executing main.py...
recipes folder found. Skipping scraper execution.
Running matcher...
Found 2 matching recipes.
Matching recipes:
  - https://ricette.giallozafferano.it/Crepes-dolci-e-salate-ricetta-base.html
  - https://ricette.giallozafferano.it/Besciamella.html
Matching completed.
Pipeline completed successfully!
```

## Troubleshooting

- **Permission denied**: Make sure `run_pipeline.sh` is executable: `chmod +x run_pipeline.sh`
- **No recipes found**: Check that your `fridge.json` contains ingredients that match recipe requirements
- **Scraping issues**: The scraper will only run when the `recipes/` folder is missing



