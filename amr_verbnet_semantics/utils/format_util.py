"""
Utility functions for formatting
"""
import inspect


def to_json(obj):
    if isinstance(obj, dict):
        results = {}
        for key in obj:
            results[key] = to_json(obj[key])
        return results
    elif isinstance(obj, list):
        results = []
        for elem in obj:
            results.append(to_json(elem))
        return results
    elif isinstance(obj, DictObject):
        results = {}
        for key in dir(obj):
            if key.startswith('_'):
                continue
            results[key] = to_json(getattr(obj, key))
        return results
    elif hasattr(obj, "to_json") and inspect.ismethod(getattr(obj, "to_json")):
        return obj.to_json()
    else:
        return obj


class DictObject(object):
    def __init__(self, in_dict):
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictObject(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, DictObject(val) if isinstance(val, dict) else val)

