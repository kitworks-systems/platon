import html

from platon.constants import TransactionType, PURCHASE_URL, URLS
from platon.params import FrozenParams


class Form:
    ACTION_URL = PURCHASE_URL

    TEMPLATE = (
        '<form method="post" action="{action}" accept-charset="utf-8">\n'
        '    {param_inputs}\n'
        '    <input type="submit" value="Submit purchase form">\n'
        '</form>'
    )
    INPUT_TEMPLATE = '<input type="hidden" name="{name}" value="{value}" />'

    def __init__(self, key, password, params: dict):
        self.key = key
        self.password = password
        self.params = FrozenParams(self.key, self.password, TransactionType.PURCHASE, params)

    def get_inputs(self):
        inputs = []
        for param_name, param_value in self.params.items():
            if param_name not in ["transactionType"]:
                if isinstance(param_value, (list, tuple)):
                    for item in param_value:
                        inputs.append(self.render_input(f'{param_name}[]', item))
                else:
                    inputs.append(self.render_input(param_name, param_value))
        return inputs

    def render(self):
        return self.TEMPLATE.format(
            action=self.ACTION_URL,
            param_inputs='\n    '.join(self.get_inputs())
        )

    def render_input(self, name, value):
        return self.INPUT_TEMPLATE.format(name=name, value=html.escape(str(value)))


class GetParams:
    def __init__(self, key, password: str, transaction_type: TransactionType, params: dict):
        self.key = key
        self.password = password
        self.url = URLS[transaction_type]
        self.params = FrozenParams(self.key, self.password, transaction_type, params)

    def data(self):
        prepared_params = {'action_url': self.url, 'params': {}}
        for param_name, param_value in self.params.items():
            if param_name not in ["transactionType"]:
                prepared_params['params'][param_name] = param_value
        return prepared_params
