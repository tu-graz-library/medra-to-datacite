import os
from functools import wraps

from lxml import etree


def xsd_ns(localname: str) -> etree.QName:
    return etree.QName(os.getenv("NS"), localname)


def debug(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if os.getenv("DEBUG") == "True":
            print(f"debug: {fn.__name__}")
        return fn(*args, **kwargs)

    return wrapper
