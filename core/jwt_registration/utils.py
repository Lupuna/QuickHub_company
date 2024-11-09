from rest_framework.exceptions import ValidationError


def get_email_or_400(request):
    email = request.data.get('email')
    if not email:
        raise ValidationError({'error': 'User creation not initiated'})
    return email