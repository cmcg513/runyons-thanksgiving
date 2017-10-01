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

    def clean(self, value):
        """
        Validate value as per usual, and then parse
        """
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        try:
            parsed = parse(value,'US')
        except NumberParseException:
            raise ValidationError('Please enter a valid phone number, e.g. ' \
                '(555) 555-5555')
        except Exception:
            raise ValidationError('We\'re sorry, but something went wrong. ' \
                'Enter your phone number again')

        phone_number = str(parsed.national_number)
        if len(phone_number) < 10:
            raise ValidationError('The phone number provided must have at ' \
                'least 10 digits. Please ensure you provide an area code')
        return phone_number
