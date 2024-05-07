import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd

def setup_driver():
    options = Options()
    options.headless = True  # Set to False to observe the behavior, True for production
    driver = webdriver.Chrome(options=options)
    return driver

def search_bestbuy_selenium(driver, product_name):
    driver.get("https://www.bestbuy.com")
    try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.us-link"))
            ).click()
            print("USA link selected successfully.")
    except Exception as e:
        print(f"Failed to select USA: {e}")
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gh-search-input'))
        )
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h4.sku-title'))
        )
        product_title = driver.find_element(By.CSS_SELECTOR, 'h4.sku-title').text
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.priceView-hero-price.priceView-customer-price'))
        )

        price = price_element.text
        # Clean the price using regex to extract only the essential price part
        match = re.search(r'\$\d+\.\d+', price)
        if match:
            price = match.group()

        # Return data as a dictionary
        return {
            'Site': 'BestBuy.com',
            'Item title name': product_title,
            'Price(USD)': price
        }
    except Exception as e:
        print(f"Error while extracting data: {e}")
        return None
    
# Newegg search using requests and BeautifulSoup
def scrape_newegg(product_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    search_url = f"https://www.newegg.com/p/pl?d={product_name}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product_element = soup.select_one('.item-title')
    if product_element:
        product_title = product_element.text
        price_element = soup.select_one('.price-current')
        price = price_element.text.split()[0] if price_element else 'Price not found'
        return {'Site': 'Newegg.com', 'Item title name': product_title, 'Price(USD)': price}
    return None


def search_walmart(product_name):
    url = "https://www.walmart.com/search/?query=" + product_name
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check if any results were found
    no_results = soup.select_one('.search-no-results')
    if no_results:
        return {
            'Site': 'Walmart.com',
            'Item title name': 'Product title not found',
            'Price(USD)': 'Price not found'
        }
    
    # CSS selector for the search results header
    product_title = soup.select_one('span[data-automation-id="product-title"]')
    if product_title:
        product_title = product_title.text.strip()  # Get the full title text
    else:
        product_title = "Product title not found"
    
    # CSS selectors for price
    price_main = soup.select_one('div[aria-hidden="true"] span.f2')
    price_decimal = soup.select_one('div[aria-hidden="true"] span.f6.f5-l[style="vertical-align:0.75ex"]')
    if price_main and price_decimal:
        price = f"${price_main.text.strip()}.{price_decimal.text.strip()}"
    else:
        price = "Price not found"
    
    return {'Site': 'Walmart.com', 'Item title name': product_title, 'Price(USD)': price}

# Main function to execute the combined search
def combined_search(product_name):
    driver = setup_driver()

    bestbuy_data = search_bestbuy_selenium(driver, product_name)
    newegg_data = scrape_newegg(product_name)
    walmart_data = search_walmart(product_name)
    
    driver.quit()

    results = [d for d in [bestbuy_data, newegg_data, walmart_data] if d is not None]
    return pd.DataFrame(results)

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    results_table = combined_search(product_name)
    print(results_table.to_string(index=False))