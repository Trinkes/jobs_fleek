from typing import Any

from pydantic import BaseModel, ConfigDict


class BasicModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        from_attributes=True,
    )


class Model(BasicModel):
    id: Any = None
