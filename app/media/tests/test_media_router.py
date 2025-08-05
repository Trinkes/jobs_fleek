from starlette.testclient import TestClient

from app.media.api.schemas import MediaOut
from app.media.media_status import MediaStatus


def test_create_media(test_client: TestClient):
    prompt = "test prompt"
    body = {"prompt": prompt}
    response = test_client.post("/media/generate", json=body)
    assert response.status_code == 200, response.text
    media = MediaOut.model_validate_json(response.text)
    assert media.status.job_id is not None
    assert media.id is not None
    assert media.prompt == prompt
    assert media.status.status == MediaStatus.IN_QUEUE


def test_get_media_status(test_client: TestClient):
    prompt = "test prompt"
    body = {"prompt": prompt}
    response = test_client.post("/media/generate", json=body)
    assert response.status_code == 200, response.text
    media = MediaOut.model_validate_json(response.text)

    response = test_client.get(f"/media/status/{media.status.job_id}")
    assert response.status_code == 200, response.text

    media_response = MediaOut.model_validate_json(response.text)
    assert media_response == MediaOut.model_validate(media.model_dump())
