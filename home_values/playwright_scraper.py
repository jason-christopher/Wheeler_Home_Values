from playwright.sync_api import sync_playwright
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
            print("it worked")

            # Go back to the previous page
            page.go_back(wait_until="load")

        browser.close()


if __name__ == "__main__":
    main()

