import os

import requests
import stripe
from dotenv import load_dotenv

load_dotenv()

class StripeAPI:
    url_header: str = 'https://api.stripe.com/v1/'
    api_key = os.getenv('STRIPE_API_KEY')

    def products(self) -> list:
        url = self.url_header + 'products'
        response = requests.get(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key})
        if response.ok:
            return response.json().get('data')
        else:
            return []

    def prices(self) -> list:
        url = self.url_header + 'prices'
        response = requests.get(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key})
        if response.ok:
            return response.json().get('data')
        else:
            return []

    def del_product_by_index(self, ind: int = 0) -> int:
        prods = self.products()
        url = self.url_header + 'products/' + prods[ind].id
        response = requests.delete(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key})
        return response.status_code

    def del_product_by_id(self, id: str) -> int:
        url = self.url_header + 'products/' + id
        response = requests.delete(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key})
        return response.status_code

    def product_price(self, product_id: str):
        url = self.url_header + 'prices/search'
        query = f"product: '{product_id}'"
        response = requests.get(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key,}, params={'query': query})
        return response

