try:
    import json5 as json
except ImportError:
    import json

import os


class Json:
    @staticmethod
    def load(path: str, **kwargs) -> dict | list:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f, **kwargs)

    @staticmethod
    def dump(path: str, data: dict | list, utf8: bool = True, **kwargs):
        assert "ensure_ascii" not in kwargs, "ensure_ascii is not allowed"
        if "indent" not in kwargs:
            kwargs["indent"] = 2
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=utf8, **kwargs)

    @staticmethod
    def update(path: str, data: dict | list, utf8: bool = True, **kwargs):
        old = Json.load(path, **kwargs)
        old.update(data)

        Json.dump(path, old, utf8=utf8, **kwargs)

    @staticmethod
    def append(path: str, data: dict | list, utf8: bool = True, **kwargs):
        old = Json.load(path, **kwargs)

        if isinstance(old, list):
            old.extend(data)
        else:
            old.update(data)

        Json.dump(path, old, utf8=utf8, **kwargs)

    @staticmethod
    def touch(path: str, default: dict | list = {}):
        if not os.path.exists(path):
            Json.dump(path, default)
