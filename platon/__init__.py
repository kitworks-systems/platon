from urllib.parse import urljoin, urlencode


from platon.api import Api
from platon.constants import TransactionType, PURCHASE_URL
from platon.generators import Form, GetParams
from platon.params import FrozenParams


__all__ = ['Platon']


class Platon:
    def __init__(self, key, password):
        self.key = key
        self.password = password
        self.api = Api(self.key, self.password)

    def get_form(self, params: dict):
        return Form(self.key, self.password, params)

    def get_params(self, transaction_type: TransactionType, params: dict):
        return GetParams(self.key, self.password, transaction_type, params)
