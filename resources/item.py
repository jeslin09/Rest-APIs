from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt
from schemas import ItemSchema, ItemsUpdateSchema
from models import ItemModel
from db import db

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item
    @jwt_required()
    def delete(self, item_id):
        jwt=get_jwt()
        if not jwt.get("is_admin"):
            abort(401,message="cannot delete")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return{"message":'Item deleted'},200

    @blp.arguments(ItemsUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if(item):
            item.price=item_data["price"]
            item.name=item_data["name"]
        else:
            item=ItemModel(id=item_id, **item_data)
        db.session.add(item)
        db.session.commit()   
        return item     
    
        '''if not item:
            abort(404, message="Item not found.")

        for key, value in item_data.items():
            setattr(item, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the item.")

        return item
'''

@blp.route("/item")
class ItemList(MethodView):

    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item
