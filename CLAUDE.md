# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UFC Predictor is a Python-based project for scraping UFC fighter statistics from ufcstats.com and building a machine learning model to predict fight outcomes. The project is in early development with a completed scraper and a prediction model in progress.

## Python Environment

- Python 3.12+ (project uses 3.12.1)
- Virtual environment: `.venv/` (activate with `source .venv/bin/activate` on macOS/Linux)
- No requirements.txt or pyproject.toml exists yet - dependencies are installed manually

### Key Dependencies
- beautifulsoup4: HTML parsing
- requests: HTTP requests (note: uses a custom `basic_request` wrapper, not standard requests library)
- pandas, numpy, scikit-learn: Data processing and ML
- pint: Unit conversions (height/weight/reach)
- icecream: Debugging

## Project Structure

### scrape-ufc.py
The main scraper that extracts fighter data from ufcstats.com. This file is complete and tested.

**Architecture:**
1. `get_fighters()`: Iterates through alphabet (a-z) to collect all fighter profile URLs from index pages
2. `extract_fighter_pagelinks()`: Parses HTML to extract unique fighter profile links
3. `get_n_extract_fighter_data()`: Fetches individual fighter pages and extracts data
4. `extract_fighter_data()`: Main extraction orchestrator that calls bio and career extraction
5. `extract_bio()`: Parses physical attributes (height, weight, reach, stance, DOB) with conversion to metric
6. `extract_career()`: Parses career statistics (striking, takedown, submission stats)
7. `executer()`: Main entry point that orchestrates the full scraping pipeline

**Missing Utility Functions:**
The scraper imports several utility functions that don't exist in the repository:
- `basic_request(url, logger)`: HTTP request wrapper (from requests module)
- `setup_basic_file_paths(project_name)`: Returns file paths for data/logs
- `setup_logger(log_file_path)`: Logger configuration
- `save_ndjson(data, file_path)`: Saves data in NDJSON format
- `format_error(exception)`: Error message formatting

These utilities need to be created or the imports fixed before the scraper can run.

**Output:**
- Saves to `data/fighter_data.ndjson` (exact path determined by `setup_basic_file_paths`)
- Each line is a JSON object with fighter data

**Debug Flags:**
- `RUN_ONLY_ONE = False`: Process only first letter (for testing)
- `RUN_25_ITR = True`: Process only first 25 fighters (currently enabled for testing)
- `IS_IC_DEBUG = False`: Enable icecream debug output

### predict.py
Machine learning model for predictions - incomplete (only 11 lines of imports and partial pandas read statement).

## Data Schema

Each fighter record contains:
- **Identity**: name, nickname
- **Record**: wins, losses, draws
- **Physical**: height_cm, weight_kg, reach_cm, stance, dob (date of birth)
- **Striking**: ss_landed_per_minute, ss_accuracy, ss_absorbed_per_min, ss_defence
- **Grappling**: avg_td_per_15, td_accuracy, td_defence, avg_sub_attempt_per_15

All measurements are converted to metric (cm, kg). Missing/invalid data ("--") is converted to None.

## Running the Code

**Before first run:**
1. Create missing utility module with: basic_request, setup_basic_file_paths, setup_logger, save_ndjson, format_error
2. OR fix imports in scrape-ufc.py to use actual available libraries
3. Create requirements.txt with all dependencies

**To run the scraper:**
```bash
source .venv/bin/activate
python scrape-ufc.py
```

**Note:** The scraper has no if __name__ == "__main__" block, so executer() must be called manually or added.

## Development Practices

- Logging is used extensively via the LOGGER global variable
- Error handling: Individual fighter failures are caught and logged but don't stop execution
- Unit conversions are handled inline (imperial to metric) using pint library
- BeautifulSoup CSS selectors are used for HTML parsing
- Data extraction uses defensive programming with try/except blocks for missing fields
