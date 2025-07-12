"""
API for working with api.stripe.com online payments services provider
"""
import os

import requests
import stripe
from dotenv import load_dotenv

load_dotenv()


class StripeAPI:
    url_header: str = 'https://api.stripe.com/v1/'
    api_key = os.getenv('STRIPE_API_KEY')

    def create_product(self, name: str, description: str = ''):
        url = self.url_header + 'products'
        response = requests.post(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key},
                                 params={'name': name, 'description': description})
        if response.ok:
            return response.json()
        else:
            return None

    def create_price(self, product_id: str, amount: int, currency: str = 'rub'):
        url = self.url_header + 'prices'

        # price = stripe.Price.create(
        #     currency="usd",
        #     unit_amount=1000,
        #     recurring={"interval": "month"},
        #     product_data={"name": "Gold Plan"},
        # )
        response = requests.post(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key},
                                 params={'product': product_id, 'currency': currency, 'unit_amount': amount * 100})
        if response.ok:
            return response.json()
        else:
            return None

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
        response = requests.get(url, headers={'Authorization': 'Bearer ' + StripeAPI.api_key, },
                                params={'query': query})
        return response

    def create_checkout_session(self, price_id: str, success_url: str = "https://example.com/success"):
        stripe.api_key = StripeAPI.api_key
        session = stripe.checkout.Session.create(
            success_url=success_url,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
        )
        return session

    def checkout_session(self, session_id: str):
        stripe.api_key = StripeAPI.api_key
        session = stripe.checkout.Session.retrieve(session_id)
        return session
