from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

def generic_email_access_token(user_id, email):
    s = Serializer(settings.SECRET_KEY, expires_in=24 * 60 * 60)

    token = s.dumps({
        'id': user_id,
        'email': email
    })

    access_token = token.decode()
    return access_token