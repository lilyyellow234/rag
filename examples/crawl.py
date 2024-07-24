import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# Ref: https://selenium-python.readthedocs.io/locating-elements.html

BASE_URL = "https://glosbe.com/zh/vi"
CONTENT = "中央通讯社，简称中央社，是中华民国的国家通讯社。1924年4月1日由中国国民党在广州成立，1949年随中华民国政府播迁台湾。1996年依据《中央通讯社设置条例》从公司转为由中华民国政府捐助成立的财团法人机构%5Ba%5D，改制为国家通讯社%5B2%5D。目前总社设于台北市中山区的志清大楼%5B3%5D"
TRANSLATE_URL = f"{BASE_URL}/{CONTENT}"
WAIT_TIMEOUT = 1 # wait for some seconds

# Allow a pop-up window to be in cognito mode
chrome_options = Options()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)

# Specify the URL to get the data from
driver.get(TRANSLATE_URL)

# Scroll to the end of the page and wait for some seconds
# so that the page can be fully loaded
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(WAIT_TIMEOUT)

NUMBER_LOAD = 5
count = 0
while True:
    try:
        # Scroll to the end of the page and wait for some seconds
        # so that the page can be fully loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(WAIT_TIMEOUT)
        # Locate the "LOAD MORE" button
        show_more_button = driver.find_element(By.XPATH, '//button[text()="LOAD MORE"]')
        # Click on it
        print("Click `LOAD MORE` button")
        show_more_button.click()
        # # Sleep for some seconds for loading items
        # time.sleep(WAIT_TIMEOUT)
    except NoSuchElementException:
        # If the "LOAD MORE" button is not found, break the loop
        print("No more 'LOAD MORE' button found. The page is fully loaded.")
        break
    except ElementClickInterceptedException:
        # If the button is not clickable at the moment, wait and try again
        print("Button not clickable, retrying...")
        time.sleep(WAIT_TIMEOUT)

    if count > NUMBER_LOAD:
        break
    
    count += 1

# Wait for a while to be fully loaded
time.sleep(WAIT_TIMEOUT)

# Scrape the current page by BeautifulSoup
page = BeautifulSoup(driver.page_source, features="html.parser")

# Find all elements using the specified class
elements = page.find_all("div", class_="odd:bg-slate-100 px-1")
logger.info(f"Num of elements: {len(elements)}")

# Prepare lists to store product names for each language
texts_zh = []
texts_vi = []

# Process each element
for element in elements:
    try:
        # Find the div with the class "w-1/2 dir-aware-pr-1 dense" and lang attribute "zh"
        text_zh = element.find("div", class_="w-1/2 dir-aware-pr-1 dense", lang="zh").get_text()
        texts_zh.append(text_zh)
        
        # Find the div with the class "w-1/2 dir-aware-pl-1 " and lang attribute "vi"
        text_vi = element.find("div", class_="w-1/2 dir-aware-pl-1", lang="vi").get_text()
        texts_vi.append(text_vi)
        
    except Exception as e:
        logger.warning(f"Error processing element: {e}")
        continue

# Create a DataFrame with the collected product names
df = pd.DataFrame({
    'text_zh': texts_zh,
    'text_vi': texts_vi
})

# Define the destination path for the CSV file
dest = "./zh_vi_texts.csv"

# Write the DataFrame to the CSV file
if os.path.exists(dest):
    # If the file already exists, append to it
    df.to_csv(dest, mode="a", index=False, header=False)
else:
    # Else, create a new file and write to it
    df.to_csv(dest, mode="w", index=False, header=True)

logger.info(f"Data written to {dest}")


