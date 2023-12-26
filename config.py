import tomllib
from collections.abc import MutableMapping

from constants import CONFIG_FILE


class AttrDict(MutableMapping):
    """
    A dictionary that allows for attribute-style access.
    """

    def __init__(self, *args, **kwargs):
        self.__dict__["_data"] = dict(*args, **kwargs)

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError(f"'AttrDict' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        # self._data[key] = value
        raise NotImplementedError("Not supported")

    def __delattr__(self, item):
        # del self._data[item]
        raise NotImplementedError("Not supported")

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        # self._data[key] = value
        raise NotImplementedError("Not supported")

    def __delitem__(self, key):
        # del self._data[key]
        raise NotImplementedError("Not supported")

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"{type(self).__name__}({self._data})"


def to_attrdict(obj):
    if isinstance(obj, dict):
        return AttrDict({k: to_attrdict(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return [to_attrdict(v) for v in obj]
    else:
        return obj


class Config(AttrDict):
    def __init__(self, config_path=CONFIG_FILE):
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        super().__init__(to_attrdict(data))
