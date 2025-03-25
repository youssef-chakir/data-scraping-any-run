import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Ensure 'data' directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# Read URLs from file (assumes a file named 'urls_trojan.txt' exists)
with open("urls_trojan.txt", "r") as file:
    urls = [line.strip() for line in file.readlines()]

# Configure Edge WebDriver with anti-detection settings
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Launch Edge WebDriver
driver = webdriver.Edge(options=options)

# Remove navigator.webdriver detection
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Define section names in the desired order
section_names = [
    "general info",
    "behavior activities",
    "process information",
    "registry activity",
    "files activity",
    "network activity"
]

# Define XPaths for standard sections
sections = {
    "general info": '//*[@id="app"]/div[3]/div[2]/div/section[1]',
    "behavior activities": '//*[@id="app"]/div[3]/div[2]/div/section[2]',
    "registry activity": '//*[@id="app"]/div[3]/div[2]/div/section[7]',
    "files activity": '//*[@id="app"]/div[3]/div[2]/div/section[8]',
    "network activity": '//*[@id="app"]/div[3]/div[2]/div/section[9]',
}

# Define XPaths for process information
process_main_xpath = '//*[@id="app"]/div[3]/div[2]/div/section[6]/div[2]/div/div[5]'
excluded_table_xpath = '//*[@id="app"]/div[3]/div[2]/div/section[6]/div[2]/div/div[5]/div[1]/table'

# Scrape each URL
for i, url in enumerate(urls, start=1):
    print(f"Scraping page {i}: {url}")
    try:
        driver.get(url)
        # Random delay to mimic human behavior
        time.sleep(random.uniform(3, 7))

        # Initialize list to hold section texts
        section_texts = []

        # Extract content for each section
        for section_name in section_names:
            if section_name == "process information":
                # Special handling for process information
                try:
                    # Locate the main process information section
                    main_section = driver.find_element(By.XPATH, process_main_xpath)
                    # Find all tables with IDs starting with "table-processes-"
                    process_tables = main_section.find_elements(By.XPATH, './/*[starts-with(@id, "table-processes-")]')
                    # Try to find the table from which to exclude the second row
                    try:
                        excluded_table = driver.find_element(By.XPATH, excluded_table_xpath)
                    except NoSuchElementException:
                        excluded_table = None

                    process_text_list = []
                    # Process each table
                    for table in process_tables:
                        table_html = table.get_attribute('outerHTML')
                        soup = BeautifulSoup(table_html, 'html.parser')
                        # If this is the table to modify, remove the second row
                        if excluded_table and table == excluded_table:
                            rows = soup.find_all('tr')
                            if len(rows) >= 2:
                                rows[1].decompose()  # Remove the second <tr> element
                        # Extract text with newlines separating table content
                        text = soup.get_text(separator='\n').strip()
                        process_text_list.append(text)

                    # Combine text from all tables
                    process_info_text = '\n\n'.join(process_text_list) if process_text_list else "No process tables found"
                    section_texts.append(f"section {section_name} :\n{process_info_text}")
                except NoSuchElementException:
                    section_texts.append(f"section {section_name} : Section not found")
            else:
                # Handle standard sections
                try:
                    xpath = sections[section_name]
                    element = driver.find_element(By.XPATH, xpath)
                    text = element.text.strip()  # Extract plain text, no HTML
                    section_texts.append(f"section {section_name} :\n{text}")
                except NoSuchElementException:
                    section_texts.append(f"section {section_name} : Section not found")

        # Write structured output to a text file
        with open(f"data/page{i}.txt", "w", encoding="utf-8") as file:
            file.write('\n\n\n\n'.join(section_texts))
        print(f"✅ Saved: data/page{i}.txt")

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")

    # Random delay before next URL
    time.sleep(random.uniform(5, 10))

# Close the browser
driver.quit()
print("✅ Scraping complete.")