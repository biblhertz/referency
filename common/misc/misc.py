from common.misc import fields
from frozendict import frozendict
import re


def broom(data):
    """
    Sanitizes data

    :param data: a dict containing key,value pairs to broom

    :return: cleaned data
    """
    if data is None:
        return data

    def clean(txt: str):
        NON_ALPHA_NUMERIC = r'[^\w]'

        if txt:
            return re.sub(NON_ALPHA_NUMERIC, ' ', txt).strip()

        else:
            return None

    if type('') == type(data):
        return clean(data)
    elif type([]) == type(data):
        return [clean(d) for d in data]
    elif type({}) == type(data):
        for i, (key, value) in enumerate(data.items()):
            assert (key in fields.ALL)
            if type(data[key]) is type([]):
                for idx, value in enumerate(data[key]):
                    data[key][idx] = clean(value)
            else:
                data[key] = clean(value)
        return data


def fill_with_none(data):
    for f in fields.ALL:
        if f not in data:
            data[f] = None

    return data

def freeze(obj: dict):
    for key, value in obj.items():
        if type([]) == type(value):
            obj[key] = frozenset(value)

    return frozendict(obj)