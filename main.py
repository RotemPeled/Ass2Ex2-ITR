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
    
    # Using the specific selectors for dollars and cents
    dollars_selector = '#\\30  > section > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div.flex.flex-wrap.justify-start.items-center.lh-title.mb1 > div.b.black.mr1.lh-copy.f5.f4-l > span.f2'
    cents_selector = '#\\30  > section > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div.flex.flex-wrap.justify-start.items-center.lh-title.mb1 > div > span:nth-child(4)'
    
    link_element = soup.select_one('a[href*="/ip/"]')  # Generalized to find any product link containing "/ip/"
    title_element = link_element.find_parent('div').select_one('span') if link_element else None  # Assuming title is in a span within the same div as the link
    
    dollars_element = soup.select_one(dollars_selector)
    cents_element = soup.select_one(cents_selector)
    
    if link_element and title_element and dollars_element and cents_element:
        product_url = "https://www.walmart.com" + link_element.get('href', '')
        product_title = title_element.text.strip()
        # Combine dollars and cents
        price = f"${dollars_element.text.strip()}.{cents_element.text.strip()}"
        
        return {'Site': 'Walmart.com', 'Item title name': product_title, 'Price(USD)': price, 'Link': product_url}

    return {'Site': 'Walmart.com', 'Error': 'Product details not found'}


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
