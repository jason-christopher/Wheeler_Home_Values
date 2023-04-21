# Wheeler Home Values Scraper

Author: Jason Christopher  
Version: 2.0

This is a web scraper designed to collect home values and other relevant information from the Oklahoma County Assessor Public Access System. The data collected will be written to an output CSV file, which can be further analyzed using the provided Jupyter Notebook.

## Prerequisites

- Python 3.11 or later
- Playwright
- Jupyter Notebook

**NOTE:** Ensure that you have the correct location of the Chromium executable on your system. Update the `executable_path` parameter in the line below to match your local setup:

```
browser = p.chromium.launch(executable_path="/Users/kaylachristopher/Library/Caches/ms-playwright/chromium-1041/chrome-mac/Chromium.app/Contents/MacOS/Chromium", headless=False, timeout=5000)
```

## Installation

1. Clone the repo down to your local machine using the `git clone` command.
2. `cd` into the newly created directory.
3. Create a virtual environment by running: `python3.11 -m venv .venv`
   * **NOTE:** Replace `python3.11` with more specific version as needed.
4. Activate the virtual environment by running: `source .venv/bin/activate`
5. Install all required dependencies by running: `pip install -r requirements.txt`

## Run the Program

1. Inside the `home_values` directory, modify ***Line 10*** of the `playwright_scraper.py` file to fill the list with a range of addresses you'd like to scrape.
   * Use the `%` character as a wildcard to expand your search.
2. Update the `executable_path` parameter in the line below to match your local setup (if not already done):

```
browser = p.chromium.launch(executable_path="/Users/kaylachristopher/Library/Caches/ms-playwright/chromium-1041/chrome-mac/Chromium.app/Contents/MacOS/Chromium", headless=False, timeout=5000)
```

3. Run `python home_values/playwright_scraper.py`
4. A new Chromium window should open for you to follow along and the terminal will update with the scraped data.
5. Once all the address data has been collected, the data will be written to the `output.csv` file in the root level.
6. A Jupyter Notebook can be accessed in the `analysis.ipynb` file in the root level to perform more machine learning analysis.
   * To run, click the double-green-arrow **Run All** button.
   * You can update the Python list at the bottom of the notebook to predict the market value and sales price based on the desired input values.

## Resources

- [Oklahoma County Assessor Public Access System](https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp)

## Support

For any questions or concerns, please contact the author at [jchristopher2448@gmail.com](mailto:jchristopher2448@gmail.com).