from playwright.sync_api import sync_playwright  # 'pip install pytest-playwright' and then 'playwright install chromium'
from playwright.sync_api import Playwright, Page
import csv
import re


def main():

    # Modify the list below to create a list of street addresses you'd like to scrape. The '%' character is a wildcard.
    addresses = ["%%%% Pedalers Ln", "1%%% Pioneer St", "1%%% Runway Blvd", "1%%% Oso Ave", "10%% SW 16th St", "181% Wheeler St", "182% Wheeler St", "183% Wheeler St", "%%%% Hangar Dr"]
    address_list = []

    # Open a new CSV file for writing
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = ['address', 'square_feet', 'market_values', 'sales_prices', 'year_built', 'bedrooms', 'bathrooms', 'garage_sqft', 'garage_apt_sqft', 'porch_sqft', 'unfin_attic_sqft']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterates through the address list
        for address_range in addresses:

            # Starts the playwright script and launches a Chromium window to follow along
            with sync_playwright() as p:
                # browser = p.chromium.launch(executable_path="/Users/kaylachristopher/Library/Caches/ms-playwright/chromium-1041/chrome-mac/Chromium.app/Contents/MacOS/Chromium", headless=False, timeout=5000)
                browser = p.chromium.launch(headless=False, timeout=5000)
                page = browser.new_page()
                page.goto("https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp", wait_until="domcontentloaded")

                # Finds the Physical Address section and adds the address range
                input_field = page.locator("input[name='FormattedLocation']")
                input_field.fill(address_range)

                # Clicks the Submit button
                cell = page.get_by_role("cell", name="Submit Reset Example: 110 E Main.....or 1% E Main (must include street direction or use wildcard option) Wildcard searches are available using \"%\" or only a portion of the block # and a portion of the street name")
                submit_button = cell.get_by_role("button", name="Submit")
                submit_button.click()

                # Find the fourth table and all the <a> elements inside it
                links_in_fourth_table = page.locator("table:nth-child(4) a")
                link_elements = links_in_fourth_table.element_handles()

                for i in range(len(link_elements)):

                    # Find the fourth table and all the <a> elements inside it
                    links_in_fourth_table = page.locator("table:nth-child(4) a")
                    link_elements = links_in_fourth_table.element_handles()

                    # Check if there are any more links to click
                    if i >= len(link_elements):
                        break

                    # Clicks on each individual address link
                    link = link_elements[i]
                    page.on("dialog", lambda dialog: dialog.dismiss())
                    link.click()
                    page.wait_for_load_state("load")

                    # Collects the full street address and confirms it hasn't been previously searched
                    address_raw = page.locator("table:nth-child(4) tr:nth-child(1) td:nth-child(5) p").inner_text()
                    address_parts = address_raw.split(",")
                    address = address_parts[0].strip()
                    if address not in address_list:
                        address_list.append(address)
                        print("Address: ", address)

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
                        print("   Market Values: ", market_values)

                        # Collect sale prices
                        num_rows2 = len(page.locator("table:nth-child(10) tr").element_handles())
                        sales_prices = {}
                        for row in range(1, num_rows2 - 1):
                            try:
                                date = page.locator(f"table:nth-child(10) tr:nth-child({row}) td:nth-child(1) p").inner_text(timeout=2000)
                                date_clean = int(date[-4:])
                                sales_price = page.locator(f"table:nth-child(10) tr:nth-child({row}) td:nth-child(6) p").inner_text(timeout=2000)
                                sales_price_clean = int(sales_price.replace(',', ''))
                                if sales_price_clean > 150000 and date_clean not in sales_prices:
                                    sales_prices[date_clean] = sales_price_clean
                            except Exception as e:
                                print(f"   Error encountered while trying to collect sales prices: {e}")
                        print("   Sales Prices: ", sales_prices)

                        try:
                            table = page.locator('table:nth-child(13)')
                            inner_html = table.inner_html()
                            num_td_elements = inner_html.count('<td')
                            if num_td_elements > 1:
                                more_detail_link = page.locator("table:nth-child(13) a")
                                more_detail_link.click()
                                page.wait_for_load_state("load")

                                # Collect square footage
                                try:
                                    sq_feet = int(
                                        page.locator("table:nth-child(4) tr:nth-child(1) td:nth-child(1) table:nth-child(1) tr:nth-child(5) td:nth-child(2) font").inner_text(
                                            timeout=2000).replace(',', ''))
                                    print("   Square Feet: ", sq_feet)
                                except Exception as e:
                                    print(f"   Error encountered while trying to collect square footage: {e}")
                                    sq_feet = None

                                # Collect year built
                                try:
                                    year_built = int(
                                        page.locator(
                                            "table:nth-child(4) tr:nth-child(1) td:nth-child(1) table:nth-child(1) tr:nth-child(6) td:nth-child(2) font").inner_text(
                                            timeout=2000).replace(',', ''))
                                    print("   Year Built: ", year_built)
                                except Exception as e:
                                    print(f"   Error encountered while trying to collect year built: {e}")
                                    year_built = None

                                # Collect number of bedrooms
                                try:
                                    bedrooms_text = page.locator("table:nth-child(4) tr:nth-child(1) td:nth-child(1) table:nth-child(1) tr:nth-child(20) td:nth-child(2) font").inner_text(timeout=2000).replace(',', '')
                                    bedrooms_match = re.search(r'\(\s*(\d+)\s*\).*?(\d+)', bedrooms_text)
                                    if bedrooms_match:
                                        bedrooms = int(bedrooms_match.group(2))
                                        print(f"   Bedrooms: {bedrooms}")
                                    else:
                                        bedrooms = None
                                        print(f"   Bedrooms: Unknown")
                                except Exception as e:
                                    print(f"   Error encountered while trying to collect number of bedrooms: {e}")
                                    bedrooms = None

                                # Collect number of bathrooms
                                try:
                                    bathrooms_text = page.locator("table:nth-child(4) tr:nth-child(1) td:nth-child(1) table:nth-child(1) tr:nth-child(21) td:nth-child(2) font").inner_text(timeout=2000).replace(',', '')
                                    bathrooms = re.findall(r'\((\d+)\)', bathrooms_text)
                                    full_bathrooms = int(bathrooms[0]) + int(bathrooms[1])
                                    half_bathrooms = int(bathrooms[2]) / 2
                                    bathrooms = full_bathrooms + half_bathrooms
                                    print(f"   Bathrooms: {bathrooms}")
                                except Exception as e:
                                    print(f"   Error encountered while trying to collect number of bathrooms: {e}")
                                    bathrooms = None

                                # Collect garage, garage apartment, unfinished attic, and porch square footage
                                garage_sqft = 0
                                porch_sqft = 0
                                garage_apt_sqft = 0
                                ua_sqft = 0
                                try:
                                    table = page.locator('table:nth-child(5)')
                                    inner_html = table.inner_html()
                                    num_tr_elements = inner_html.count('<tr')
                                    for tr in range(1, num_tr_elements - 1):
                                        td_text = page.locator(f"table:nth-child(5) tr:nth-child({tr}) td:nth-child(2) p").inner_text(timeout=2000)
                                        if "GarApart" in td_text:
                                            garage_apt_sqft_text = page.locator(f"table:nth-child(5) tr:nth-child({tr}) td:nth-child(4) p").inner_text(timeout=2000)
                                            garage_apt_sqft += int(garage_apt_sqft_text)
                                        if "Gar" in td_text:
                                            garage_sqft_text = page.locator(f"table:nth-child(5) tr:nth-child({tr}) td:nth-child(4) p").inner_text(timeout=2000)
                                            garage_sqft += int(garage_sqft_text)
                                        if "Por" in td_text:
                                            porch_sqft_text = page.locator(f"table:nth-child(5) tr:nth-child({tr}) td:nth-child(4) p").inner_text(timeout=2000)
                                            porch_sqft += int(porch_sqft_text)
                                        if "UA" in td_text:
                                            ua_sqft_text = page.locator(f"table:nth-child(5) tr:nth-child({tr}) td:nth-child(4) p").inner_text(timeout=2000)
                                            ua_sqft += int(ua_sqft_text)
                                    print(f"   Garage Apt Sq Footage: {garage_apt_sqft}")
                                    print(f"   Garage Sq Footage: {garage_sqft}")
                                    print(f"   Porch Sq Footage: {porch_sqft}")
                                    print(f"   Unfinished Attic Sq Footage: {ua_sqft}")
                                except Exception as e:
                                    print(f"   Error encountered while trying to collect garage and porch square footage: {e}")
                                    garage_sqft = 0
                                    porch_sqft = 0
                                    garage_apt_sqft = 0
                                    ua_sqft = 0

                                # Go back to previous page
                                page.go_back(wait_until="load")

                            else:
                                pass
                        except Exception as e:
                                print(f"   Error encountered while trying to collect more details: {e}")


                        # Write to CSV file
                        writer.writerow({'address': address, 'square_feet': sq_feet, 'market_values': market_values, 'sales_prices': sales_prices, 'year_built': year_built, 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'garage_sqft': garage_sqft, 'garage_apt_sqft': garage_apt_sqft, 'porch_sqft': porch_sqft, 'unfin_attic_sqft': ua_sqft})

                        # Reset all values
                        address = sq_feet = market_values = sales_prices = year_built = bedrooms = bathrooms = full_bathrooms = half_bathrooms = garage_sqft = garage_apt_sqft = porch_sqft = ua_sqft = half_bathrooms = None

                    # Go back to the previous page
                    page.go_back(wait_until="load")

                browser.close()

        print("Successfully collected all address data!")


if __name__ == "__main__":
    main()
