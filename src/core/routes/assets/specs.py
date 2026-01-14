#import os
#from datetime import datetime, timedelta

from src.core.decorators.decorators import require_jwt
from flask import Blueprint, render_template, request, make_response, jsonify

assets_blueprint = Blueprint("assets", __name__)

@assets_blueprint.get("/tmp-assets")
def get_login():
    return render_template("tmp-assets.html")

@assets_blueprint.post("/tmp-assets") #temporary TMP
def insert_asset():
    data = request.form.to_dict()
    print(data)
    return {"oui?": "en effet"}
