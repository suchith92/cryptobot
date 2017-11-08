import requests
import base64, hashlib, hmac, time
from requests.auth import AuthBase
import json

def products():
    # sandbox api base
    api_base = 'https://api-public.sandbox.gdax.com'
    response = requests.get(api_base + '/products')
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' %response.status_code)
    return response.json()

class GDAXRequestAuth(AuthBase):
    def __init__(self,api_key, secret_key,passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'),hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'CB-ACCESS-SIGN' : signature_b64,
            'CB-ACCESS-TIMESTAMP' : timestamp,
            'CB-ACCESS-KEY' : self.api_key,
            'CB-ACCESS-PASSPHRASE' : self.passphrase,
            'Content-Type' : 'application/json'
        })
        return request


def buy_market(product_id, size):
    auth = GDAXRequestAuth(api_key, api_secret, passphrase)
    order_data = {
        'type': 'market',
        'side': 'buy',
        'product_id': product_id,
        'size': size
    }
    response = requests.post(api_base + '/orders', data=json.dumps(order_data), auth=auth)
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
    return response.json()


def buy_limit(product_id, price, size, time_in_force='GTC', cancel_after=None, post_only=None):
    auth = GDAXRequestAuth(api_key, api_secret, passphrase)
    order_data = {
        'type': 'market',
        'side': 'buy',
        'product_id': product_id,
        'size': size,
        'time_in_force':time_in_force
    }
    if 'time_in_force' is 'GTT':
        order_data['cancel_after'] = cancel_after
    if 'time_in_force' not in ['IOC','FOK']:
        order_data['post_only']=post_only
    response = requests.post(api_base + '/orders',data=json.dumps(order_data), auth=auth)
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
    return response.json()


def order_status(order_id):
    order_url = api_base + '/orders/' + order_id
    response = requests.get(order_url, auth=auth)
    if response.status_code is not 200:
        raise Exception('Invalid  GDAX Status Code: %d' % response.status_code)
    return response.json()

if __name__ == "__main__":
    api_base = 'https://api-public.sandbox.gdax.com'
    api_key = '637963ff851b6409c3c2c715abfe7ecc'
    api_secret = 'hmIZU7fjOq50yW/eH+WkCcPh2Wdjqf8Lk4/6/J0PBPCne5bKC1Gj6cznQcGdp0QMI/01dIJVwYweAkIEUm5Twg=='
    passphrase = 'hobbe$C01N'

    auth = GDAXRequestAuth(api_key, api_secret, passphrase)
    order_url = api_base + '/orders'
    order_data = {
        'type': 'market',
        'side': 'buy',
        'product_id': 'BTC-USD',
        'size': '0.01'
    }
    response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
    print(response.json())