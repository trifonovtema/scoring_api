import logging
import subprocess

import pytest
from redis import Redis
from src.store import Store
from src.handler import method_handler
from src.settings import Responses
from datetime import datetime
import pytest
import docker
import time
from redis import Redis
import subprocess
import os

from tests.utils import set_valid_auth


@pytest.fixture
def context():
    return {}


def test_method_handler_empty_request(store, headers, context):
    request = {"body": {}, "headers": headers}
    response, code = method_handler(request, context, store)

    assert code == Responses.INVALID_REQUEST
    assert "Request body is empty" in response


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
def test_online_score_success(request_data, store, headers, context):
    set_valid_auth(request_data)
    request = {"body": request_data, "headers": headers}
    response, code = method_handler(request, context, store)

    assert code == Responses.OK
    assert "score" in response
    assert response["score"] == 3.5


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
        },
    ],
)
def test_clients_interests_success(
    request_data,
    store,
    headers,
    context,
    prepopulated_redis_interests,
):

    set_valid_auth(request_data)

    request = {"body": request_data, "headers": headers}
    response, code = method_handler(request, context, store)

    assert code == Responses.OK
    assert response == {1: ["sports", "movies"], 2: ["music", "books"]}


def test_store_cache_operations(store):
    store.cache_set("test_key", 42.0, 60)
    result = store.cache_get("test_key")
    assert float(result) == 42.0


def test_store_operations(store, prepopulated_redis_values):
    assert store.get("key1") == "10"
    assert store.get("key2") == "20"


def test_store_reconnect(store):
    store.client = None
    store.connect()

    assert store.client is not None
    store.client.set("test_key", "value")
    assert store.client.get("test_key") == "value"
