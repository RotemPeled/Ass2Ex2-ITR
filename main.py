import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def setup_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    return driver

def search_bestbuy_selenium(driver, product_name):
    driver.get("https://www.bestbuy.com")
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.us-link"))
        ).click()
    except Exception as e:
        print(f"Failed to select USA: {e}")

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gh-search-input'))
        )
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.sku-item'))
        )
        product_element = driver.find_element(By.CSS_SELECTOR, 'li.sku-item')
        product_title = product_element.find_element(By.CSS_SELECTOR, 'h4.sku-title').text
        product_url = product_element.find_element(By.CSS_SELECTOR, 'a.image-link').get_attribute('href')
        price_element = product_element.find_element(By.CSS_SELECTOR, 'div.priceView-hero-price.priceView-customer-price')
        price = price_element.text
        match = re.search(r'\$\d+\.\d+', price)
        if match:
            price = match.group()
        return {'Site': 'BestBuy.com', 'Item title name': product_title, 'Price(USD)': price, 'Link': product_url}
    except Exception as e:
        print(f"Error while extracting data: {e}")
        return None

def scrape_newegg(product_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://www.newegg.com/p/pl?d={product_name}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product_element = soup.select_one('.item-cell')  # Ensure we get the right container element
    if product_element:
        title_element = product_element.select_one('.item-title')
        product_title = title_element.text if title_element else "Title not found"
        product_url = title_element['href'] if title_element else None  # Ensure URL is retrieved directly from the title element

        price_element = product_element.select_one('.price-current')
        price = price_element.text.strip().split()[0] if price_element else 'Price not found'
        return {'Site': 'Newegg.com', 'Item title name': product_title, 'Price(USD)': price, 'Link': product_url}
    return None

def search_walmart(product_name):
    url = f"https://www.walmart.com/search/?query={product_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    product_title_element = soup.select_one('span[data-automation-id="product-title"]')
    if product_title_element:
        product_title = product_title_element.text.strip()
        link_element = soup.select_one('a[data-automation-id="product-title-link"]')
        product_url = "https://www.walmart.com" + link_element.get('href') if link_element else None

        price_main = soup.select_one('div[aria-hidden="true"] span.f2')
        price_decimal = soup.select_one('div[aria-hidden="true"] span.f6.f5-l[style="vertical-align:0.75ex"]')
        price = f"${price_main.text.strip()}.{price_decimal.text.strip()}" if price_main and price_decimal else "Price not found"
        
        return {'Site': 'Walmart.com', 'Item title name': product_title, 'Price(USD)': price, 'Link': product_url}
    return None




@app.get("/search/{product_name}")
async def search(product_name: str):
    driver = setup_driver()
    try:
        bestbuy_data = search_bestbuy_selenium(driver, product_name)
        newegg_data = scrape_newegg(product_name)
        walmart_data = search_walmart(product_name)
    finally:
        driver.quit()

    results = [d for d in [bestbuy_data, newegg_data, walmart_data] if d is not None]
    if not results:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
