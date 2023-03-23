from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import pandas as pd
from parser import parse

# pip install pytest-playwright
# playwright install chromium


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/Users/kaylachristopher/Library/Caches/ms-playwright/chromium-1041/chrome-mac/Chromium.app/Contents/MacOS/Chromium", headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto("https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp", wait_until="domcontentloaded")

        # Find the input field using its selector (e.g., using an ID, class, or other attribute)
        input_field = page.locator("input[name='FormattedLocation']")  # Replace #input-field with the actual selector
        input_field.fill("1%%% Pioneer St")

        cell = page.get_by_role("cell",
                                name="Submit Reset Example: 110 E Main.....or 1% E Main (must include street direction or use wildcard option) Wildcard searches are available using \"%\" or only a portion of the block # and a portion of the street name")
        submit_button = cell.get_by_role("button", name="Submit")
        submit_button.click()

        # Find the fourth table and all the <a> elements inside it
        links_in_fourth_table = page.locator("table:nth-child(4) a")

        # Get the elements
        link_elements = links_in_fourth_table.element_handles()

        # Open a new CSV file for writing
        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = ['address', 'square_feet', 'market_values', 'sales_prices']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(len(link_elements)):
                # Find the fourth table and all the <a> elements inside it
                links_in_fourth_table = page.locator("table:nth-child(4) a")

                # Get the elements
                link_elements = links_in_fourth_table.element_handles()

                # Check if there are any more links to click
                if i >= len(link_elements):
                    break

                link = link_elements[i]
                page.on("dialog", lambda dialog: dialog.dismiss())
                link.click()
                page.wait_for_load_state("load")

                # Perform any actions or extract information from the new page
                address = page.locator("table:nth-child(4) tr:nth-child(1) td:nth-child(5) p").inner_text()
                print(address)

                # Collect square footage
                try:
                    sq_feet = int(page.locator("table:nth-child(13) tr:nth-child(1) td:nth-child(6) p").inner_text(timeout=2000).replace(',', ''))
                    print(sq_feet)
                except Exception as e:
                    print(f"Error encountered while trying to collect square footage: {e}")
                    sq_feet = None

                # Collect annual market values
                num_rows1 = len(page.locator("table:nth-child(7) tr").element_handles())
                market_values = {}
                for row in range(1, num_rows1 - 1):
                    year = int(page.locator(f"table:nth-child(7) tr:nth-child({row}) td:nth-child(1) p").inner_text())
                    market_value = page.locator(f"table:nth-child(7) tr:nth-child({row}) td:nth-child(2) p").inner_text()
                    market_value_clean = int(market_value.replace('\xa0', '').replace(',', ''))
                    if market_value_clean > 100000:
                        market_values[year] = market_value_clean
                    else:
                        break
                print(market_values)

                # Collect sale prices
                num_rows2 = len(page.locator("table:nth-child(10) tr").element_handles())
                sales_prices = {}
                for row in range(1, num_rows2 - 1):
                    date = page.locator(f"table:nth-child(10) tr:nth-child({row}) td:nth-child(1) p").inner_text()
                    date_clean = int(date[-4:])
                    sales_price = page.locator(f"table:nth-child(10) tr:nth-child({row}) td:nth-child(6) p").inner_text()
                    sales_price_clean = int(sales_price.replace(',', ''))
                    if sales_price_clean > 150000 and date_clean not in sales_prices:
                        sales_prices[date_clean] = sales_price_clean
                print(sales_prices)

                # Write to CSV file
                writer.writerow({'address': address, 'square_feet': sq_feet, 'market_values': market_values, 'sales_prices': sales_prices})

                # Go back to the previous page
                page.go_back(wait_until="load")

        browser.close()


if __name__ == "__main__":
    main()

