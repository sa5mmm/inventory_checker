from bs4 import BeautifulSoup
import requests

# url = "https://wholesalepet.com/Product/181859"
url = "https://wholesalepet.com/Product/132858"

response = requests.get(url)

content = response.text

soup = BeautifulSoup(content)

body = list(soup.children)[-2]

add_to_cart = list(body.children)

