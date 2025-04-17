from Domain import authBusiness, SensorDataPublisher
from Infrastructure import ProcedureCall


def login(request):
    auth = request.authorization
    if not auth:
        return None, "missing creadentials", 401

    result = ProcedureCall.Authenticate(auth.username, auth.password)

    if len(result) > 0:
        user_name = result[0]
        password = result[1]

        if auth.username != user_name or auth.password != password:
            return None, "invalid credentials", 401
        else:
            SensorDataPublisher.SensorDataPublish(request.remote_addr)
            return authBusiness.createJWT(auth.username, 'secret', True), None

    else:
        return None, "invalid creadentials", 401

