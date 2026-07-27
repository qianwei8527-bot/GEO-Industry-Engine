import os
from typing import Any


class WeightsLoader:
    _cache: dict = {}

    @classmethod
    def load(cls, name: str) -> dict:
        if name in cls._cache:
            return cls._cache[name]
        path = os.path.join("config", "scoring", f"{name}.yaml")
        if not os.path.exists(path):
            cls._cache[name] = {}
            return {}
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        weights = {}
        in_weights = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped == "weights:":
                in_weights = True
                continue
            if in_weights:
                if stripped.startswith("thresholds:") or stripped == "":
                    in_weights = False
                    continue
                if ":" in stripped:
                    parts = stripped.split(":", 1)
                    key = parts[0].replace("- ", "").strip()
                    try:
                        val = float(parts[1].strip())
                        weights[key] = val
                    except ValueError:
                        pass
        cls._cache[name] = weights
        return weights
