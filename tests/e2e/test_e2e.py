import pytest
import requests
from datetime import datetime
from src.settings import Responses
from tests.utils import set_valid_auth


def test_e2e_empty_request(base_url, wait_for_healthcheck):
    response = requests.post(f"{base_url}/method", json={})
    assert response.status_code == 422
    assert "Request body is empty" in response.json()["error"]


@pytest.mark.parametrize(
    "request_data",
    [
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "arguments": {
                "phone": "79175002040",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        },
    ],
)
def test_e2e_online_score(request_data, base_url, docker_redis, wait_for_healthcheck):
    set_valid_auth(request_data)
    response = requests.post(f"{base_url}/method", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "response" in response_data
    assert response_data["response"]["score"] == 3.5


@pytest.mark.parametrize(
    "request_data",
    [
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "clients_interests",
            "arguments": {
                "client_ids": [1, 2],
                "date": datetime.now().strftime("%d.%m.%Y"),
            },
            "token": "VALID_TOKEN",
        },
    ],
)
def test_e2e_clients_interests(
    request_data,
    base_url,
    docker_redis,
    wait_for_healthcheck,
    prepopulated_redis_interests,
):
    set_valid_auth(request_data)
    response = requests.post(f"{base_url}/method", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "response" in response_data
    assert response_data["response"] == {
        "1": ["sports", "movies"],
        "2": ["music", "books"],
    }
