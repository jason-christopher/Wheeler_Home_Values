# Oklahoma County Property Scraper

This script scrapes property information such as address, square footage, market values, and sales prices from [Oklahoma County's property records website](https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp). The data is saved to a CSV file and then analyzed using machine learning in a Jupyter Notebook within this repo.

## Author: Jason Christopher

## Version: 1.0

### Installation

1. Clone the repo down to your local machine using the `git clone` command.
2. `cd` into the newly created directory.
3. Create a virtual environment by running: `python3.11 -m venv .venv`
   * **NOTE:** Replace `python3.11` with more specific version as needed.
4. Activate the virtual environment by running: `source .venv/bin/activate`
5. Install all required dependencies by running: `pip install -r requirements.txt`

### Run the Program

1. Inside the `home_values` directory, modify ***Line 10*** of the `playwright_scraper.py` file to fill the list with a range of addresses you'd like to scrape. 
   * Use the `%` character as a wildcard to expand your search.
2. Run `python home_values/playwright_scraper.py`
3. A new Chromium window should open for you to follow along and the terminal will update with the scraped data.
4. Once all the address data has been collected, the data will be written to the `output.csv` file in the root level.
5. A Jupyter Notebook can be accessed in the `analysis.ipynb` file in the root level to perform more machine learning analysis. 
   * **Note:** Currently in progress and needs more work, but the basics are there!
   * To run, click the double-green-arrow **Run All** button.
   * You will receive a prompt to input a **square footage** (an integer) to predict market value and sales price based on the homes in the analysis.

### Resources

* Oklahoma County Assessor Public Access System



