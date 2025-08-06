from pydantic import Field

from app.core.model import BasicModel
from app.media.media import Media


class MediaGenerationParams(BasicModel):
    prompt: str


class MediaOut(Media):
    media_uri: str | None = Field(None, exclude=True)
