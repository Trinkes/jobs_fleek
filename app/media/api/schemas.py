from app.core.model import BasicModel
from app.media.media import Media


class MediaGenerationParams(BasicModel):
    prompt: str


class MediaOut(Media):
    pass
