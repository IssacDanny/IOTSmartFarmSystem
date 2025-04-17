
from flask import jsonify
from Infrastructure import ProcedureCall

def registration(request):
    # Get the data from the request
    data = request.get_json()

    # Extract the user details
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    device_name = data.get('device_name')

    # Validation
    if not username or not email or not password or not device_name:
        return jsonify({"error": "Missing required fields"}), 400

    #check if user have existed
    count, err = ProcedureCall.FindUser(username, email)
    if count is None:
        return err

    if count > 0:
        return jsonify({"error": "Username or Email already exists"}), 400

    # Call the stored procedure to insert data into Users and Devices table
    return ProcedureCall.RegistUser(username, password, email, device_name)
