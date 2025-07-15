# import stripe
#
# from rest_framework.reverse import reverse

from materials.stripe_api import StripeAPI
from users.models import Payment

api = StripeAPI()


def test_create_product():
    result = api.create_product('test product', 'product desc')
    assert True
    return result


def test_create_price():
    product = test_create_product()
    result = api.create_price(product['id'], 50000)
    assert True
    return result


def test_create_checkout_session():
    session = api.create_checkout_session('price_1RjL8804SatfhYz2xG37YPoJ')
    assert True
    return session
#
#
# def test_list_products():
#     result = api.products()
#     print(result)
#     assert True
#
#
# def test_del_product():
#     pass
#     # prods = api.products()
#     # prices = api.prices()
#     # stripe.api_key = StripeAPI.api_key
#     # for prod in prods:
#     #     price_data = api.product_price(prod['id'])
#     #     if price_data.status_code == 200:
#     #         price_id = price_data.json()['data'][0]['id']
#     #         api.change_price(price_id, 5000000)
#     #         # url = api.link_to_buy()
#     #         # print(f"url to buy: {url}")
#     #     else:
#     #         api.del_product_by_id(prod['id'])
