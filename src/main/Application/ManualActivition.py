import json
from Domain import authBusiness
def activateDevice(request):
    # check authorization before perform task
    authorized, err = authBusiness.validate(request)

    if err:
        return err

    authorized = json.loads(authorized)  # the json file of token

    # TODO: implement logic for communicate with cloud to activate hardware
    return