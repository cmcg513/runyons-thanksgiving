from django import forms
from django.core.exceptions import ValidationError
from phonenumbers import parse, NumberParseException

class PhoneField(forms.CharField):
    """
    Django form field to validate and parse phone numbers for the US
    """

    def __init__(self, max_length=None, min_length=None, strip=True, empty_value='', *args, **kwargs):
        """
        Initialize CharField base
        """

        super(PhoneField, self).__init__(
            max_length,
            min_length,
            strip,
            empty_value,
            *args,
            **kwargs)
        self.validators.append(validate_phone_number)

    def clean(self, value):
        """
        Validate value as per usual, and then parse
        """
        # print("CLEAN")
        # print(value)
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        # print("BEFORE parse")
        phone_number = parse(value,'US')
        return phone_number.national_number

def validate_phone_number(value):
    # print("VALIDATE")
    # print(value)
    try:
        parse(value,'US')
    except NumberParseException:
        raise ValidationError('%s is not a valid phone number' % value)
    except Exception:
        raise ValidationError('%s could not be validated' % value)
