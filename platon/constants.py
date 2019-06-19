from enum import Enum

PURCHASE_URL = 'https://secure.platononline.com/payment/auth'
INVOICE_URL = 'https://pltn.me/v1/'
SUPPORTED_LANGUAGES = ['RU', 'UK', 'EN']
SUPPORTED_PAYMENT = ['CC', 'CCT', 'RF']
SUPPORTED_CURRENCY = ['UAH', 'USD', 'EUR']


class TransactionType(str, Enum):
    PURCHASE = 'PURCHASE'
    CONFIRM_PURCHASE = 'CONFIRM_PURCHASE'
    CREATE_INVOICE = 'CREATE_INVOICE'
    CHECK_STATUS = 'CHECK_STATUS'


SIGNATURE_FIELDS = {
    TransactionType.PURCHASE: [
        'key',
        'payment',
        'data',
        'url',
        'password',
    ],
    TransactionType.CONFIRM_PURCHASE: [
        'email',
        'password',
        'order',
        'card',
    ],
    TransactionType.CREATE_INVOICE: [
        'key',
        'order',
        'amount',
        'password',
    ],
}
SIGNATURE_REVERSED_FIELDS = {
    TransactionType.PURCHASE: [
        'key',
        'payment',
        'data',
        'url',
        'password',
    ],
    TransactionType.CONFIRM_PURCHASE: [
        'email',
        'card',
    ],
    TransactionType.CREATE_INVOICE: [
        'password'
    ],
}
REQUIRED_FIELDS = {
    TransactionType.PURCHASE: [
        'key',
        'payment',
        'data',
        'url',
    ],
    TransactionType.CONFIRM_PURCHASE: [],
    TransactionType.CREATE_INVOICE: [
        'key',
        'order',
        'action',
        'description',
        'amount',
    ],
}
NEED_MAKE_FIELDS = {
    TransactionType.PURCHASE: {
        'data': [
            'amount',
            'currency',
            'description',
        ],
    },
    TransactionType.CONFIRM_PURCHASE: [],
    TransactionType.CREATE_INVOICE: [],
}

URLS = {
    TransactionType.PURCHASE: 'https://secure.platononline.com/payment/auth',
    TransactionType.CONFIRM_PURCHASE: 'https://secure.platononline.com/payment/auth',
    TransactionType.CREATE_INVOICE: 'https://pltn.me/v1/',
}
