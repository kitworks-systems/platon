from functools import partialmethod

import requests

from platon.params import FrozenParams
from platon.constants import URLS, TransactionType


class Api:
    def __init__(self, merchant_account, merchant_key):
        self.merchant_account = merchant_account
        self.merchant_key = merchant_key

    def _query(self, transaction_type: TransactionType, params: dict):
        URL = URLS[transaction_type]
        params = FrozenParams(self.merchant_account, self.merchant_key, transaction_type, params)
        response = requests.post(URL, json=params)
        return response.json()

    create_invoice = partialmethod(_query, TransactionType.CREATE_INVOICE)
