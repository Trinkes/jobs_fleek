from starlette.testclient import TestClient

from app.media.api.schemas import MediaOut
from app.media.media_status import MediaStatus


def test_media_router(test_client: TestClient):
    prompt = "test prompt"
    body = {"prompt": prompt}
    response = test_client.post("/media/generate", json=body)
    assert response.status_code == 200, response.text
    media = MediaOut.model_validate_json(response.text)
    assert media.job_id is not None
    assert media.id is not None
    assert media.prompt == prompt
    assert media.status == MediaStatus.IN_QUEUE
