import os
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, render_template, request, make_response, jsonify

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

@auth_blueprint.get("/login")
def get_login():
    return render_template("login.html")

@auth_blueprint.post("/login")
def post_login():
    data = request.form.to_dict()
    #user = get_user_by_email(data["email"])
    #
    # if not user:
    #     return jsonify({
    #         'message': 'Email or password incorrect',
    #     }), 401
    # if not verify_password(password, user.Password):
    #     return jsonify({
    #         'message': 'Email or password incorrect',
    #     }), 401
    #############################################################
    # Temporaire
    if data['email'] == "test@p5stock.fr" and data['password'] == "Sup€rP@ssw0rd":
        access_payload = {
            'user_id': "ububhbo",
            'exp': datetime.utcnow() + timedelta(minutes=10),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        access_token = jwt.encode(access_payload, os.getenv("JWT_SECRET"), algorithm='HS256')
        response = make_response(jsonify({
            'message': 'Login successful',
        }), 200)
        response.set_cookie('access_token', access_token, httponly=True, max_age=10 * 60)
        return response
    return jsonify({
             'message': 'Email or password incorrect',
         }), 401
    ################################################################