import hashlib
from datetime import datetime

from src.fields import (
    CustomField,
    ClientIDsField,
    DateField,
    CharField,
    EmailField,
    PhoneField,
    BirthDayField,
    GenderField,
    ArgumentsField,
)
from src.settings import SecuritySettings


class ValidationMeta(type):
    def __new__(cls, name, bases, dct):
        dct["_fields"] = {}
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, CustomField):
                dct["_fields"][attr_name] = attr_value
                attr_value.field_name = attr_name
        return super().__new__(cls, name, bases, dct)


class Validatable(metaclass=ValidationMeta):
    _fields: dict

    def __init__(self, **kwargs):
        self.errors = []
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name)

            if field.required and field_name not in kwargs:
                self.errors.append(f"Field '{field_name}' is required")

            if not field.nullable and value is None:
                self.errors.append(f"Field '{field_name}' cannot be None")

            setattr(self, field_name, value)

    def is_valid(self) -> int:
        return len(self.errors) == 0


class ClientsInterestsRequest(Validatable):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __str__(self):
        return f"{self.client_ids=} {self.date=}"


class OnlineScoreRequest(Validatable):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __str__(self):
        return f"{self.first_name=} {self.last_name=} {self.email=} {self.phone=} {self.birthday=}"


class MethodRequest(Validatable):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == SecuritySettings.ADMIN_LOGIN

    def check_auth(self):
        if self.is_admin:
            digest = hashlib.sha512(
                (
                    datetime.now().strftime("%Y%m%d%H") + SecuritySettings.ADMIN_SALT
                ).encode("utf-8")
            ).hexdigest()
        else:
            digest = hashlib.sha512(
                (self.account + self.login + SecuritySettings.SALT).encode("utf-8")
            ).hexdigest()

        return digest == self.token
