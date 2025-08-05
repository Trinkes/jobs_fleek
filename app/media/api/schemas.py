from pydantic.json_schema import SkipJsonSchema

from app.core.model import BasicModel
from app.media.media import Media


class MediaGenerationParams(BasicModel):
    prompt: str


class MediaOut(Media):
    media_uri: SkipJsonSchema[str] | None = None
