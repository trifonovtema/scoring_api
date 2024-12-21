from dataclasses import dataclass


@dataclass
class LogSettings:
    LOG_FILE_PATH: str | None = None  # "./scoring_api.log"


@dataclass
class SecuritySettings:
    SALT = "Otus"
    ADMIN_LOGIN = "admin"
    ADMIN_SALT = "42"


@dataclass
class Responses:
    OK = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INVALID_REQUEST = 422
    INTERNAL_ERROR = 500
    ERRORS = {
        BAD_REQUEST: "Bad Request",
        FORBIDDEN: "Forbidden",
        NOT_FOUND: "Not Found",
        INVALID_REQUEST: "Invalid Request",
        INTERNAL_ERROR: "Internal Server Error",
    }


@dataclass
class GenderSettings:
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDERS = {
        UNKNOWN: "unknown",
        MALE: "male",
        FEMALE: "female",
    }
