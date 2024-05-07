from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re

def setup_driver():
    options = Options()
    options.headless = True  # Set to False to observe the behavior, True for production
    driver = webdriver.Chrome(options=options)
    return driver

def select_country(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.us-link"))
        ).click()
        print("USA link selected successfully.")
    except Exception as e:
        print(f"Failed to select USA: {e}")

def search_bestbuy_selenium(driver, product_name):
    driver.get("https://www.bestbuy.com")
    select_country(driver)

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gh-search-input'))
        )
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.ENTER)  # Ensure the search is executed by simulating the Enter key

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h4.sku-title'))
        )
        product_title = driver.find_element(By.CSS_SELECTOR, 'h4.sku-title').text
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.priceView-hero-price.priceView-customer-price'))
        )

        price= price_element.text
        # Clean the price using regex to extract only the essential price part
        match = re.search(r'\$\d+\.\d+', price)
        if match:
            price = match.group()


        # Create a DataFrame to display the data
        data = {
            'Site': 'BestBuy.com',
            'Item title name': [product_title],
            'Price(USD)': [price]
        }
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error while extracting data: {e}")
        return None

def main():
    product_name = input("Please enter the product name to search on Best Buy: ")
    driver = setup_driver()
    product_info = search_bestbuy_selenium(driver, product_name)
    if product_info is not None:
        print(product_info)
    else:
        print("Failed to extract product details.")
    driver.quit()

if __name__ == "__main__":
    main()