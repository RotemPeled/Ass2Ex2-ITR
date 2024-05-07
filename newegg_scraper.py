import requests
from bs4 import BeautifulSoup

def scrape_newegg(product_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    search_url = f"https://www.newegg.com/p/pl?d={product_name}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product_element = soup.select_one('.item-title')
    if not product_element or 'href' not in product_element.attrs:
        return "Product not found"
    
    product_url = product_element['href']
    product_response = requests.get(product_url, headers=headers)
    product_soup = BeautifulSoup(product_response.text, 'html.parser')

    price_element = product_soup.select_one('.price-current')
    if not price_element:
        return "Price not found"
    
    return {
        'Site': 'Newegg',
        'Item title name': product_element.get_text(strip=True),
        'Price(USD)': price_element.get_text(strip=True).split()[0]  # Assumes price is first item
    }

# Example usage
product_name = input("Enter the product name: ")
print(scrape_newegg(product_name))
