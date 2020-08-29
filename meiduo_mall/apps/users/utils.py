from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
from apps.users.models import User

def generic_email_access_token(user_id, email):
    s = Serializer(settings.SECRET_KEY, expires_in=24 * 60 * 60)

    token = s.dumps({
        'id': user_id,
        'email': email
    })

    access_token = token.decode()
    return access_token

def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user