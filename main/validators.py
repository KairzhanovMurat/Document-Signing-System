from django.core.exceptions import ValidationError


def validate_pdf(value):
    if not value.name.lower().endswith('.pdf'):
        raise ValidationError('File must be a PDF.')


def validate_png(value):
    if not value.name.lower().endswith('.png'):
        raise ValidationError('Image must be a PNG.')
