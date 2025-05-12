import jwt, datetime, os
from fastapi.responses import JSONResponse
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
        return None, JSONResponse(
                        status_code=401,
                        content={"error": "missing credentials"}
                    )

    encode_jwt = request.headers.get("Authorization")

    if not encode_jwt:
        return None, JSONResponse(
                        status_code=401,
                        content={"error": "missing credentials"}
                    )


    encode_jwt = encode_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encode_jwt, "secret",
            algorithms=["HS256"]
        )
    except:
        return None, JSONResponse(
                        status_code=403,
                        content={"error": "not authorized"}
                    )

    return decoded, None