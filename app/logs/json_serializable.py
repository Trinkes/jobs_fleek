import json
from datetime import datetime
from typing import Any
from uuid import UUID


def make_json_serializable(data: dict[str, Any] | list) -> dict[str, Any] | list | None:
    if data is None:
        return None

    def convert_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, UUID):
            return str(value)
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)

    if isinstance(data, dict):
        return {key: convert_value(value) for key, value in data.items()}
    elif isinstance(data, list) or isinstance(data, tuple):
        return [convert_value(value) for value in data]
    else:
        return data
