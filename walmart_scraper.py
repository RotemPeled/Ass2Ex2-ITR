import requests
from bs4 import BeautifulSoup

def search_walmart():
    product_name = input("Please enter the product name: ")
    url = "https://www.walmart.com/search/?query=" + product_name
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check if any results were found
    no_results = soup.select_one('.search-no-results')
    if no_results or not soup.select_one('.f4.f3-m.lh-title.ma0.di'):
        return {
            'Site': 'Walmart.com',
            'Item title name': 'Product title not found',
            'Price(USD)': 'Price not found'
        }
    
    # CSS selector for the search results header
    product_title = soup.select_one('.f4.f3-m.lh-title.ma0.di')
    if product_title:
        product_title = product_title.text.split('(')[0].strip()  # Splits and removes the count of results
    else:
        product_title = "Product title not found"
    
    # CSS selectors for price
    price_main = soup.select_one('.f2')
    price_decimal = soup.select_one('.f6.f5-l[style="vertical-align:0.75ex"]')
    if price_main and price_decimal:
        price = f"${price_main.text.strip()},{price_decimal.text.strip()}"
    else:
        price = "Price not found"
    
    return {
        'Site': 'Walmart.com',
        'Item title name': product_title,
        'Price(USD)': price
    }

# Example usage
print(search_walmart())
