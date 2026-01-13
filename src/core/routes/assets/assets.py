#import os
#from datetime import datetime, timedelta

from src.core.decorators.decorators import require_jwt
from flask import Blueprint, render_template, request, make_response, jsonify

assets_blueprint = Blueprint("assets", __name__)

@assets_blueprint.get("/tmp-assets")
#@require_jwt
def get_login():
    return render_template("tmp-assets.html")

@assets_blueprint.post("/tmp-assets") #temporary TMP
#@require_jwt
def insert_asset():
    data = request.form.to_dict()
    print(data)
    return {"oui?": "en effet"}


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
    # if data['email'] == "test@p5stock.fr" and data['password'] == "Sup€rP@ssw0rd":
    #     access_payload = {
    #         'user_id': "ububhbo",
    #         'exp': datetime.utcnow() + timedelta(minutes=10),
    #         'iat': datetime.utcnow(),
    #         'type': 'access'
    #     }
    #     private_key = open('private.pem', 'rb').read()
    #     access_token = jwt.encode(access_payload, private_key, algorithm='RS256')
    #     response = make_response(jsonify({
    #         'message': 'Login successful',
    #     }), 200)
    #     response.set_cookie(
    #         'access_token',
    #         access_token,
    #         httponly=True,  # Prevent XSS
    #         secure=True,  # HTTPS only (ANSSI required)
    #         samesite='Strict',  # CSRF protection (ANSSI required)
    #         max_age=10 * 60,  # 10 minutes
    #         path='/'  # Explicit path
    #     )
    #     return response
    # return jsonify({
    #          'message': 'Email or password incorrect',
    #      }), 401
    ################################################################