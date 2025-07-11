from flask import Flask, jsonify
from flask_smorest import Api
import secrets
from flask_jwt_extended import JWTManager
from db import db
import os
import models
from blocklist import BLOCKLIST
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBluePrint
from flask_migrate import Migrate


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate=Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "13b27c068530e940d1f0f10a3773cb37adf1b736066bf495672ba583a1e0a206"
    jwt=JWTManager(app)
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_eader, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    @jwt.revoked_token_loader
    def revoked_token_loader(jwt_header, jwt_payloader):
        return(
            jsonify(
                {"description":"the token has been revoked",
                "error":"token revoked"
                }
            )
        )
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "message":"The token has expired",
            "error":"token expired"
        }),401
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "message":"signature verification failed",
            "error":"invalid_token"
        }),401
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity==1:
            return {"is_Admin":True}
        return{"is_Admin":False}
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "description": "Request does not contain an access token.",
            "error": "authorization_required"
        }), 401
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required"
            }
        ), 401




    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    app.register_blueprint(TagBlueprint)
    app.register_blueprint(UserBluePrint)


    return app
