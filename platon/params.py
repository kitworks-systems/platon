import json
from collections import MutableMapping
from itertools import chain

from platon.constants import TransactionType, SUPPORTED_LANGUAGES, REQUIRED_FIELDS, SIGNATURE_FIELDS, \
    SIGNATURE_REVERSED_FIELDS, SUPPORTED_PAYMENT, NEED_MAKE_FIELDS, SUPPORTED_CURRENCY
from platon.utils import generate_signature, strrev


class ParamRequired(Exception):
    pass


class ParamReversed(Exception):
    pass


class ParamValidationError(Exception):
    pass


class ParamsBase(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = {}
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return key in self._store

    def __str__(self):
        return str(self._store)

    def __repr__(self):
        return repr(self._store)


def _val_not_empty_validator(val):
    return bool(val)


def _transaction_type_validator(val):
    try:
        TransactionType(val)
        return True
    except ValueError:
        return False


class Params(ParamsBase):
    validators = {
        **{field: _val_not_empty_validator for field in set(chain.from_iterable(REQUIRED_FIELDS.values()))},
        'transactionType': _transaction_type_validator,
        'lang': lambda x: x in SUPPORTED_LANGUAGES,
        'payment': lambda x: x in SUPPORTED_PAYMENT,
        'amount': lambda x: _val_not_empty_validator(x) and float(x) > 0,
        'description': lambda x: _val_not_empty_validator(x),
        'currency': lambda x: x in SUPPORTED_CURRENCY,
    }
    post_processors = {
        'paymentSystems': lambda x: ';'.join(x)
    }

    def get_required_fields(self) -> set:
        self._require_fields({'transactionType'})
        key = TransactionType(self['transactionType'])
        return set(REQUIRED_FIELDS[key] + self._get_signature_fields())

    def _require_fields(self, fields):
        if not isinstance(fields, set):
            fields = set(fields)
        fields.discard('password')
        if not fields.issubset(self.keys()):
            raise ParamRequired("Required param(s) not found: '{}'".format(
                ', '.join(fields - self.keys())
            ))

    def _signature_reversed_fields(self, fields):
        if not isinstance(fields, set):
            fields = set(fields)
        fields.discard('password')
        if not fields.issubset(self.keys()):
            raise ParamReversed("Reversed param(s) not found: '{}'".format(
                ', '.join(fields - self.keys())
            ))

    def _get_signature_reversed_fields(self) -> list:
        self._signature_reversed_fields({'transactionType'})
        transaction_type = TransactionType(self['transactionType'])
        return SIGNATURE_REVERSED_FIELDS[transaction_type]

    def _get_signature_fields(self) -> list:
        self._require_fields({'transactionType'})
        transaction_type = TransactionType(self['transactionType'])
        return SIGNATURE_FIELDS[transaction_type]

    def _generate_signature(self, password: str):
        signature_fields = self._get_signature_fields()
        signature_reversed_fields = self._get_signature_reversed_fields()
        self._require_fields(signature_fields)
        self._signature_reversed_fields(signature_reversed_fields)
        signature_list = []
        for item in signature_fields:
            if item == 'password':
                field = password
            elif item == 'card':
                field = self[item][0:6] + self[item][-4:]
            else:
                field = self[item]
            signature_list.append(strrev(field) if item in signature_reversed_fields else field)
        return generate_signature(signature_list)

    def _validate_field(self, field, val):
        validator = self.validators.get(field)
        if callable(validator) and not validator(val):
            raise ParamValidationError(f"Invalid param: '{field}'")

    def prepare(self, password: str):
        required_fields = self.get_required_fields()
        required_fields -= {'sign'}
        required_fields -= {'password'}
        required_fields -= {'transactionType'}
        self._require_fields(required_fields)
        self['sign'] = self._generate_signature(password)

    def _post_process(self, key, val):
        post_processor = self.post_processors.get(key)
        return post_processor(val) if callable(post_processor) else val

    def _make_param(self):
        if 'transactionType' in self:
            transaction_type = TransactionType(self['transactionType'])
            fields = NEED_MAKE_FIELDS[transaction_type]
            for field in fields:
                if field in self and bool(self[field]):
                    for key in fields[field]:
                        if key in self:
                            self.__delitem__(key)
                else:
                    make_value = {}
                    for key in fields[field]:
                        value = self.get(key)
                        if value:
                            self._validate_field(key, value)
                            make_value[key] = value
                            self.__delitem__(key)
                    if make_value:
                        self.__setitem__(field, json.dumps(make_value))

    def __setitem__(self, key, value):
        self._validate_field(key, value)
        value = self._post_process(key, value)
        super().__setitem__(key, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._make_param()


class FrozenParams(ParamsBase):
    def __init__(self, key, password: str, transaction_type: TransactionType, params: dict):
        super().__init__()
        self._store = Params(transactionType=transaction_type.value, key=key, **params)
        self._store.prepare(password)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

