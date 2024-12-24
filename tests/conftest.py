import logging
import os
import subprocess
import time
from unittest.mock import patch, MagicMock
import requests
import pytest
from redis import Redis
from src.store import Store


@pytest.fixture(scope="session")
def docker_redis():
    compose_file = None
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))

        project_root = os.path.abspath(os.path.join(current_dir, ".."))

        compose_file = os.path.join(project_root, "docker-compose.yml")
        subprocess.run(
            ["docker-compose", "-f", compose_file, "up", "--build", "-d"],
            check=True,
        )
        redis_client = None

        for _ in range(200):
            try:
                redis_client = Redis(
                    host="localhost",
                    port=6379,
                    decode_responses=True,
                )
                if redis_client.ping():
                    break
            except Exception:
                time.sleep(5)
        else:
            pytest.fail("Redis container did not become healthy")

        yield redis_client

    finally:
        try:
            subprocess.run(
                ["docker-compose", "-f", compose_file, "down"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logging.warning(f"Warning: Failed to stop containers. {e}")


@pytest.fixture(scope="session")
def wait_for_healthcheck(docker_redis):
    base_url = "http://localhost:8080/healthcheck"

    for _ in range(20):
        try:
            response = requests.get(base_url)
            if response.status_code == 200:
                logging.info("Healthcheck passed.")
                return
        except requests.ConnectionError:
            time.sleep(2)

    pytest.fail("Healthcheck did not pass.")


@pytest.fixture
def store(docker_redis):
    store = Store()
    store.client = docker_redis
    store.client.ping()
    return store


@pytest.fixture
def headers():
    return {}


@pytest.fixture
def context():
    return {}


@pytest.fixture
def mock_store(mocker):
    mock_store = MagicMock()
    mocker.patch("src.store.Store", return_value=mock_store)
    return mock_store


@pytest.fixture
def settings(mock_store):
    return mock_store


@pytest.fixture
def mock_redis():
    with patch("src.store.Redis") as MockRedis:
        yield MockRedis


@pytest.fixture(scope="function")
def prepopulated_redis_interests(docker_redis):
    docker_redis.set("i:1", '["sports", "movies"]')
    docker_redis.set("i:2", '["music", "books"]')

    yield docker_redis

    docker_redis.delete("i:1")
    docker_redis.delete("i:2")


@pytest.fixture(scope="function")
def prepopulated_redis_values(docker_redis):
    docker_redis.set("key1", 10)
    docker_redis.set("key2", 20)

    yield docker_redis

    docker_redis.delete("key1")
    docker_redis.delete("key2")


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8080"
