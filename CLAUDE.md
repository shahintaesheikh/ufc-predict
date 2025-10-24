# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UFC Predictor is a Python-based project for scraping UFC fighter and event statistics from ufcstats.com and building a machine learning model to predict fight outcomes. The project consists of two web scrapers (fighter stats and event/fight data) and a logistic regression prediction model.

## Python Environment

- Python 3.12+ (project uses 3.12.1)
- Virtual environment: `.venv/` (activate with `source .venv/bin/activate` on macOS/Linux)
- Dependencies managed via `requirements.txt`

### Key Dependencies
- beautifulsoup4: HTML parsing
- requests: HTTP requests (wrapped in custom `basic_request` utility)
- pandas, numpy, scikit-learn: Data processing and ML
- pint: Unit conversions (height/weight/reach)
- icecream: Debugging (optional)

## Project Structure

### utils.py
Shared utility functions used by both scrapers.

**Functions:**
- `basic_request(url, logger, timeout=30)`: HTTP GET wrapper with user agent headers and error handling
- `setup_basic_file_paths(project_name)`: Creates `data/`, `logs/`, `output/` directories and returns their paths
- `setup_logger(log_file_path, level=INFO)`: Configures dual logging (file + console) with timestamps
- `save_ndjson(data, file_path)`: Appends dictionary to NDJSON file
- `format_error(exception)`: Formats exceptions with full traceback for logging

### scrape-ufc.py
Scraper for individual fighter career statistics from fighter profile pages.

**Architecture Flow:**
1. `get_fighters()` → Iterates a-z to collect all fighter profile URLs
2. `extract_fighter_pagelinks(html)` → Parses index pages for unique profile links
3. `get_n_extract_fighter_data(link)` → Fetches and extracts data for one fighter
4. `extract_fighter_data(html)` → Orchestrates extraction of name, record, bio, career stats
5. `extract_bio(soup, fighter_name)` → Physical attributes (height→cm, weight→kg, reach→cm, stance, DOB)
6. `extract_career(soup, fighter_name)` → Career averages (striking/grappling stats)
7. `executer()` → Main entry point: sets up logging, runs scraper, saves to NDJSON

**Output:** `data/fighter_data.ndjson` (one JSON object per line)

**Debug Flags:**
- `RUN_ONLY_ONE = False`: Process only first letter (a)
- `RUN_25_ITR = True`: Limit to 25 fighters (currently enabled)
- `IS_IC_DEBUG = False`: Enable icecream debug output

**CSS Selector Gotchas:**
- Always include `.` prefix for class selectors (e.g., `.b-content__title-highlight`)
- BeautifulSoup must be initialized with both HTML and parser: `BeautifulSoup(html, 'html.parser')`

### scrape-ufc-events.py
Scraper for fight-level data from UFC event pages. Uses pandas DataFrame instead of NDJSON.

**Architecture:**
- Top-level script (not function-based like scrape-ufc.py)
- `extract_event_links(html)` → Extracts all event detail page URLs from completed events page
- Main loop iterates through events, then fights within each event
- Uses BeautifulSoup to parse fight rows (`td` cells with specific indices)

**Fight Details Extraction Pattern (by td index):**
- `[0]`: Win/Loss indicator (WL column)
- `[1]`: Fighter names (A and B) - uses nested `<p>` tags
- `[2]`: Knockdowns (KD) - extracts for both fighters
- `[3]`: Significant strikes (STR) - extracts for both fighters
- `[4]`: Takedowns (TD) - extracts for both fighters
- `[5]`: Submissions (SUB) - extracts for both fighters
- `[6]`: Weight class + bonus images (belt.png, fight.png, perf.png, sub.png, ko.png)
- `[7]`: Victory result/method (needs parsing into separate columns)
- `[8]`: Round number
- `[9]`: Time

**Bonus Detection:**
Images in `fight_details[6]` indicate fight bonuses. The scraper parses `src` attribute, extracts filename, and maps to binary flags (Title, Fight_Bonus, Perf_Bonus, Sub_Bonus, KO_Bonus).

**Output:** CSV file (currently hardcoded path: `/Users/da/Downloads/UFC_Events.csv`)

**Note:** Contains commented-out unused functions at top (lines 19-99). Active scraping code starts at line 101.

### predict.py
Logistic regression model for fight outcome prediction.

**Data Pipeline:**
1. Loads `fighter_data.ndjson` into pandas DataFrame
2. Drops unnecessary columns (RedFighter, BlueFighter, Date, Location, etc.)
3. Encodes categorical features:
   - Stance: Orthodox=0, Southpaw=1, Switch=2, Open Stance=3
   - Winner: Red=0, Blue=1, Draw/No Contest=2
4. Fills missing values using weight class averages (fallback to global mean)
5. Train/test split: 70/30, random_state=42
6. Standardizes features using StandardScaler
7. Trains LogisticRegression with 10-fold stratified cross-validation

**Model:** LogisticRegression(max_iter=1000)
**Evaluation:** Prints k-fold cross-validation score

## Data Schemas

### Fighter Data (scrape-ufc.py output)
Each fighter record in `fighter_data.ndjson` contains:
- **Identity**: name, nickname
- **Record**: wins, losses, draws
- **Physical**: height_cm, weight_kg, reach_cm, stance, dob (date of birth)
- **Striking**: ss_landed_per_minute, ss_accuracy, ss_absorbed_per_min, ss_defence
- **Grappling**: avg_td_per_15, td_accuracy, td_defence, avg_sub_attempt_per_15

All measurements converted to metric (cm, kg). Missing/invalid data ("--") → None.

### Event/Fight Data (scrape-ufc-events.py output)
Each fight record in CSV contains:
- **Event Info**: Event, Date, Location
- **Outcome**: WL (win/loss), Victory_Result, Victory_Method, Round, Time
- **Fighters**: Fighter_A, Fighter_B
- **Fight Stats** (per fighter): KD, STR, TD, SUB (knockdowns, strikes, takedowns, submissions)
- **Meta**: Weight_Class, Title (bool), Fight_Bonus, Perf_Bonus, Sub_Bonus, KO_Bonus (all bool)

## Running the Code

**Installation:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Scrape fighter profiles:**
```bash
python scrape-ufc.py
# Output: data/fighter_data.ndjson
# Logs: logs/scrape-ufc.log
```

**Scrape event/fight data:**
```bash
python scrape-ufc-events.py
# Output: /Users/da/Downloads/UFC_Events.csv (hardcoded path - update line 221)
```

**Train prediction model:**
```bash
python predict.py
# Requires: fighter_data.ndjson in current directory
# Prints: K-fold cross-validation score
```

## Development Practices

- **Logging**: Both scrapers use global `LOGGER` variable (initialized in executer/main)
- **Error Handling**: Individual failures logged but don't stop execution (defensive scraping)
- **Unit Conversions**: Imperial→metric via pint library (feet/inches→cm, lbs→kg)
- **HTML Parsing**: BeautifulSoup with CSS selectors (remember `.` prefix for classes!)
- **Data Storage**: scrape-ufc.py uses NDJSON (append-safe), scrape-ufc-events.py uses pandas→CSV
- **Missing Data**: Try/except blocks with None fallbacks for robustness

## Common Issues (Fixed)

1. **CSS Selectors**: Ensure `.` prefix for classes and parser specified in BeautifulSoup (`BeautifulSoup(html, 'html.parser')`)
2. ~~**Victory result/method extraction bug**: Fixed - now properly parses the text and extracts result type~~
3. ~~**Hardcoded output path**: Fixed - now saves to `data/UFC_Events.csv` relative to script location~~
4. ~~**Rate limiting**: Fixed - added 1 second delays between event requests and 0.5-1 second delays between fighter requests~~
