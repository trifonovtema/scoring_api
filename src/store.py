from time import sleep
from redis import Redis
import logging

from src.exceptions import NumberOfRetriesExceeded


class Store:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        retries: int = 2,
        timeout: int = 1,
        retry_timeout: int = 1,
    ):
        self.client: Redis | None = None
        self.host = host
        self.port = port
        self.retries = retries
        self.timeout = timeout
        self.retry_timeout = retry_timeout
        self.connect()

    def connect(self):
        logging.info(f"Trying to connect to Redis ({self.host}:{self.port})")
        for i in range(self.retries):
            try:
                self.client = Redis(
                    host=self.host,
                    port=self.port,
                    socket_timeout=self.timeout,
                    decode_responses=True,
                )
                self.client.ping()
                logging.info("Connected to Redis")
                return
            except Exception as e:
                logging.error(f"Connection attempt {i + 1}/{self.retries} failed: {e}")
                sleep(self.retry_timeout)
        raise NumberOfRetriesExceeded(
            f"Failed to connect to Redis after {self.retries} attempts"
        )

    def cache_set(
        self,
        key: str,
        value: float,
        expire_time_seconds: int | None = None,
    ) -> None:
        try:
            if self.client is not None:
                self.client.set(key, value, ex=expire_time_seconds)
        except Exception as e:
            logging.error(f"Failed to set {key} to {value}: {e}")
            return None

    def cache_get(self, key: str):
        try:
            if self.client is not None:
                return self.client.get(key)
        except Exception as e:
            logging.error(f"Failed to get cache for {key}: {e}")
            return None

    def get(self, key: str):
        try:
            if self.client is not None:
                return self.client.get(key)
        except Exception as e:
            logging.error(f"Connection error: {e}. Attempting to reconnect...")
            self.connect()
            return self.get(key)
