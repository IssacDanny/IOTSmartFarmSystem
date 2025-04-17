from flask import Flask, jsonify, request
from Application import Authentication, Registration, ManualActivition, AutomationRule
app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    token, err = Authentication.login(request)

    if not err:
        return token
    else:
        return err

@app.route("/registration", methods=["POST"])
def registration():
    return Registration.registration(request)

@app.route("/AutomationRule", methods=["POST"])
def setRule():
    return AutomationRule.setRule(request)

@app.route("/activateDevice", methods=["POST"])
def activateDevice():
    return ManualActivition.activateDevice(request)

if __name__ == "__main__":
    app.run(debug=True)
