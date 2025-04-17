import jwt, datetime, os

def createJWT(username, secret, authz):
    return jwt.encode({
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "authorized": authz,
        },
        secret,
        algorithm="HS256",
    )

def validate(request):
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    encode_jwt = request.headers("Authorization")

    if not encode_jwt:
        return None, ("missing credentials", 401)


    encode_jwt = encode_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encode_jwt, "secret",
            algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200