from users.stripe_api import StripeAPI

api = StripeAPI()

def test_list_products():

    result = api.products()
    print(result)
    assert True

def test_del_product():
    prods = api.products()
    # prices = api.prices()
    for prod in prods:
        if api.product_price(prod['id']).status_code != 200:
            api.del_product_by_id(prod['id'])