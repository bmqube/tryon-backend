import jwt

from decouple import config

JWT_SECRET = config('JWT_SECRET')


def signJWT(userId: str):
    payload = {
        'user_id': userId,
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return {
        "access_token": token,
    }


def decodeJWT(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except Exception as e:
        print(e)
        return {}
