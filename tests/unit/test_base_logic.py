import pytest
import hashlib
import datetime

from src.settings import Responses
from unittest.mock import MagicMock

from tests.utils import set_valid_auth, get_response


@pytest.mark.parametrize("request_data", [{}])
def test_empty_request(request_data, headers, context, settings):
    _, code = get_response(request_data, headers, context, settings)
    assert code == Responses.INVALID_REQUEST


@pytest.mark.parametrize(
    "request_data",
    [
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "",
            "arguments": {},
        },
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "sdd",
            "arguments": {},
        },
        {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "token": "",
            "arguments": {},
        },
    ],
)
def test_bad_auth(request_data, headers, context, settings):
    _, code = get_response(request_data, headers, context, settings)
    assert code == Responses.FORBIDDEN


@pytest.mark.parametrize(
    "request_data",
    [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ],
)
def test_invalid_method_request(request_data, headers, context, settings):
    set_valid_auth(request_data)
    response, code = get_response(request_data, headers, context, settings)
    assert code == Responses.INVALID_REQUEST
    assert len(response) > 0


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.1890",
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "XXX",
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": 1,
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "s",
            "last_name": 2,
        },
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ],
)
def test_invalid_score_request(arguments, headers, context, settings):
    request_data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "arguments": arguments,
    }
    set_valid_auth(request_data)
    response, code = get_response(request_data, headers, context, settings)
    assert code == Responses.INVALID_REQUEST
    assert len(response) > 0


@pytest.mark.parametrize(
    "arguments",
    [
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "a",
            "last_name": "b",
        },
    ],
)
def test_ok_score_request(arguments, headers, context, settings):
    request_data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "arguments": arguments,
    }
    set_valid_auth(request_data)
    response, code = get_response(request_data, headers, context, settings)

    assert code == Responses.OK
    score = response.get("score")
    assert isinstance(score, (int, float)) and score >= 0
    assert sorted(context["has"]) == sorted(arguments.keys())
