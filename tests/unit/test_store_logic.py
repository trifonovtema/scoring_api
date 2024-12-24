import pytest
import hashlib
import datetime

from src.exceptions import NumberOfRetriesExceeded
from src.settings import Responses
from unittest.mock import MagicMock, patch

from src.store import Store


def test_connect_success(mock_redis):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance

    store = Store(host="localhost", port=6379, retries=3, timeout=1, retry_timeout=0)

    mock_instance.ping.assert_called_once()
    assert store.client is not None


def test_connect_failure(mock_redis):
    mock_instance = MagicMock()
    mock_instance.ping.side_effect = ConnectionError("Unable to connect")
    mock_redis.return_value = mock_instance

    with pytest.raises(NumberOfRetriesExceeded):
        Store(host="localhost", port=6379, retries=5, timeout=1, retry_timeout=0)

    assert mock_instance.ping.call_count == 5


def test_cache_set_success(mock_redis):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance

    store = Store(host="localhost", port=6379)
    store.cache_set("key", 42.0, 60)

    mock_instance.set.assert_called_once_with("key", 42.0, ex=60)


def test_cache_set_no_client(mock_redis):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance

    store = Store(host="localhost", port=6379)
    store.client = None

    store.cache_set("key", 42.0, 60)
    mock_instance.set.assert_not_called()


def test_cache_get_success(mock_redis):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance
    mock_instance.get.return_value = "value"

    store = Store(host="localhost", port=6379)
    result = store.cache_get("key")

    mock_instance.get.assert_called_once_with("key")
    assert result == "value"


def test_cache_get_no_client(mock_redis):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance

    store = Store(host="localhost", port=6379)
    store.client = None  # Симулируем отсутствие клиента

    result = store.cache_get("key")
    assert result is None
    mock_instance.get.assert_not_called()


def test_get_reconnect_on_failure(mock_redis):
    mock_instance = MagicMock()
    mock_instance.get.side_effect = [ConnectionError("Error"), "value"]
    mock_redis.return_value = mock_instance

    store = Store(host="localhost", port=6379)
    result = store.get("key")

    assert mock_instance.get.call_count == 2
    assert result == "value"


# TODO
def test_store_connect_timeout(mock_redis):
    mock_instance = MagicMock()
    mock_instance.ping.side_effect = Exception("Timeout error")
    mock_redis.return_value = mock_instance

    with pytest.raises(NumberOfRetriesExceeded):
        Store(retries=2, timeout=0.1, retry_timeout=0.1)

    assert mock_instance.ping.call_count == 2
