import time
import os
import urllib.parse
import hashlib
import hmac
import base64
import json
import datetime

import requests

CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
APPLICATION_JSON = 'application/json'
GET = 'GET'
POST = 'POST'

class OKcoin(object):
    # Read Kraken API key and secret stored in environment variables
    api_url = "https://www.okcoin.com"
    api_key = None
    api_sec = None
    pass_phrase = None
    # api_key = "1bc30c42-779e-460a-8886-fff446d6f1a2"
    # api_sec = "BBDE37656BA9B382D2B9AE882EC79E46"
    # pass_phrase = "Anhtq@155"

    def get_okcoin_signature(self, t, method, request_path, body=None):

        if str(body) == '{}' or str(body) == 'None' or body == None:
            body = ''
        message = str(t) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.api_sec, encoding='utf8'), bytes(message, encoding='utf-8'),
                       digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    def get_header(self, sig, t):
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = self.api_key
        header[OK_ACCESS_SIGN] = sig
        header[OK_ACCESS_TIMESTAMP] = t
        header[OK_ACCESS_PASSPHRASE] = self.pass_phrase
        return header

    # Attaches auth headers and returns results of a POST request
    def okcoin_request(self, type, request_path, body=''):
        if not self.api_key:
            return
        if type == "GET":
            if body != '':
                url = '?'
                for key, value in body.items():
                    url = url + str(key) + '=' + str(value) + '&'

                body = url[0:-1]
        elif type == 'POST':
            body = json.dumps(body)
            print("NEWB: ", body)

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        signature = self.get_okcoin_signature(timestamp, type, request_path, body)
        header = self.get_header(signature, timestamp)

        # do request
        if type == 'GET':
            response = requests.get(self.api_url + request_path + body,
                    headers=header)
        else:
            print(self.api_url + request_path)
            response = requests.post(self.api_url + request_path, data=body,
                    headers=header)

        return response

    def place_order(self, volume, pair, buy_price, order_type="buy"):
        """
            Sample Response
            {'client_oid': '', 'code': '0', 'error_code': '0', 'error_message': '', 'message': '', 'order_id': '8850581166765056', 'result': True}
        """
        print("Placing order...")
        resp = self.okcoin_request(POST, '/api/spot/v3/orders', {
            "type": "limit", 
            "side": order_type, 
            "instrument_id": pair, 
            "size": volume, 
            "price": buy_price})
        
        data = json.loads(resp.content)
        print(data)

        if data['error_code'] == '0':
            if os.path.exists("orders.json"):
                with open("orders.json", "r") as f:
                    orders = json.load(f)
            else:
                orders = {}

            orders[data['order_id']] = {"pair": pair}
            with open("orders.json", "w") as f:
                json.dump(orders, f)

        print("Order placed...")
        return data

    def get_instruments(self):
        resp = self.okcoin_request(GET, "/api/spot/v3/instruments")

        return json.loads(resp.content)

    def get_balance(self):
        """
            RESP EXAMPLE
            =================
            [
                {'frozen': '0', 'hold': '0', 'id': '', 'currency': 'USD', 'balance': '30.5145258006', 'available': '30.5145258006', 'holds': '0'},
            ]
        """
        print("Getting balance...")
        # resp = self.okcoin_request(GET, "/api/spot/v3/accounts")
        resp = self.okcoin_request(GET, "/api/account/v3/wallet")
        if not resp:
            return {"code": 404}
        
        data = {"result": json.loads(resp.content)}
        data['code'] = 200
        print(data)
        return data

    def cancel_order(self, order_id):
        """
            Sample Responses
            - {'client_oid': '', 'code': '33014', 'error_code': '33014', 'error_message': 'Order does not exist', 'message': 'Order does not exist', 'order_id': '8850581166765056', 'result': False}
            - {'client_oid': '', 'code': '0', 'error_code': '0', 'error_message': '', 'message': '', 'order_id': '8850625691595776', 'result': True}
        """
        if os.path.exists("orders.json"):
                with open("orders.json", "r") as f:
                    orders = json.load(f)
        else:
            return {'error_code': 100, "message": "Failed to fetch orders"}

        instrument_id = orders[order_id]['pair']
        resp = self.okcoin_request(POST,'/api/spot/v3/cancel_orders/'+order_id, {
            "order_id": order_id,
            "instrument_id": instrument_id
        })

        data = json.loads(resp.content)
        if data['result'] == True:
            orders.pop(order_id)
            with open("orders.json", "w") as f:
                json.dump(orders, f)

        return data


if __name__ == '__main__':
    # Construct the request and print the result
    ok = OKcoin()
    resp = ok.get_balance()
    print("="*60)
    print(resp) 