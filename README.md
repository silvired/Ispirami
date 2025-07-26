# Ispirami - Recipe Recommendation System

A smart recipe recommendation system that scrapes recipes from Giallo Zafferano and matches them with ingredients available in your fridge.

## Features

- **Automatic recipe scraping** from Giallo Zafferano
- **Smart ingredient matching** based on your available ingredients
- **Conditional execution** - only scrapes when needed
- **Easy-to-use pipeline** with automatic dependency management

## Project Structure

```
ispirami/
├── main.py                 # Main pipeline orchestrator
├── matcher.py              # Recipe matching logic
├── scraper.py              # Recipe scraping from Giallo Zafferano
├── model_recipe.py         # Recipe data model
├── quantity_udm_parser.py  # Quantity and unit parsing
├── run_pipeline.sh         # Automated execution script
├── requirements.txt        # Python dependencies
├── fridge.json            # Your available ingredients
└── Recipes/               # Downloaded recipe database
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

1. **Conditional Scraping**: The system checks if the `Recipes/` folder exists
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

## Output Example

```
Starting ispirami pipeline...
Requirements installed successfully.
Executing main.py...
Recipes folder found. Skipping scraper execution.
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
- **Scraping issues**: The scraper will only run when the Recipes folder is missing



