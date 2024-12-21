from abc import ABC
from datetime import datetime, timedelta

from src.settings import GenderSettings


class CustomField(ABC):
    def __init__(self, required: bool = False, nullable: bool = False):
        self.required = required
        self.nullable = nullable
        self.field_name = None

    def __get__(self, instance, owner):
        return getattr(instance, f"_{self.field_name}_value", None)

    def __set__(self, instance, value):
        setattr(instance, f"_{self.field_name}_value", value)


class CharField(CustomField):
    def __set__(self, instance, value):
        if not isinstance(value, str) and value is not None:
            instance.errors.append(f"Field '{self.field_name}' must be a string")
        self.validate_string(instance, value)
        if value is None:
            value = ""
        super().__set__(instance, value)

    def validate_string(self, instance, value):
        pass


class ArgumentsField(CustomField):
    pass


class EmailField(CharField):
    def validate_string(self, instance, value):
        if value is not None:
            if "@" not in value:
                instance.errors.append(f"Field '{self.field_name}' must contain @")


class PhoneField(CustomField):
    def __set__(self, instance, value):
        if value is not None:
            value = str(value)
            if len(value) != 11:
                instance.errors.append(
                    f"Field '{self.field_name}' must be exactly 11 digits long"
                )

            if not value.startswith("7"):
                instance.errors.append(f"Field '{self.field_name}' must start with '7'")

            if not value.isdigit():
                instance.errors.append(
                    f"Field '{self.field_name}' must contain only digits"
                )

            super().__set__(instance, value)


class DateField(CustomField):
    def __set__(self, instance, value):
        if value is not None:
            try:
                parsed_date = datetime.strptime(value, "%d.%m.%Y")
                self.validate_date(instance, parsed_date)
                value = parsed_date
            except ValueError:
                instance.errors.append(
                    f"Field '{self.field_name}' must be in the format DD.MM.YYYY"
                )
                return

        super().__set__(instance, value)

    def validate_date(self, instance, value):
        pass


class BirthDayField(DateField):
    def validate_date(self, instance, value):
        today = datetime.now()
        seventy_years_ago = today - timedelta(days=70 * 365)
        if value < seventy_years_ago:
            instance.errors.append(
                f"Field '{self.field_name}' must not be more than 70 years ago"
            )


class GenderField(CustomField):

    def __set__(self, instance, value):
        if value is not None:
            if value not in GenderSettings.GENDERS:
                instance.errors.append("Field 'gender' must be 0, 1 or 2 ")

            super().__set__(instance, value)


class ClientIDsField(CustomField):
    def __set__(self, instance, value):
        if value is not None:
            if not isinstance(value, list):
                instance.errors.append(f"Field '{self.field_name}' must be a list")

            if len(value) == 0:
                instance.errors.append(f"Field '{self.field_name}' must not be empty")

            if not all(isinstance(item, int) for item in value):
                instance.errors.append(
                    f"Field '{self.field_name}' must contain only integers"
                )

            super().__set__(instance, value)
