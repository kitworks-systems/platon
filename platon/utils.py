import hashlib
from functools import reduce


def strrev(a_string: str) -> str:
    if isinstance(a_string, str):
        return a_string[::-1]
    else:
        raise TypeError(a_string)


def generate_signature(fields: list) -> str:
    # flatten fields
    fields = reduce(lambda x, y: x + (list(y) if isinstance(y, (list, tuple)) else [y]), fields, [])
    signature_str = ''.join(map(str, fields))
    return hashlib.md5(signature_str.upper().encode()).hexdigest()
