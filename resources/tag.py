from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema,TagAndItemSchema
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError


blp=Blueprint("Tags","tags",description="Operations On Tags")
@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store= StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)  # this tells Flask-Smorest how to serialize the TagModel
    def post(self, tag_data, store_id):
        store = StoreModel.query.get_or_404(store_id)
        tag = TagModel(**tag_data, store=store)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        
        return tag  # this works because @blp.response() handles serialization
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):

    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)  # Linking the tag to the item

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while removing the tag.")

        return {
            "message": "Item removed from tag",
            "item": item,
            "tag": tag
        }
@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        return tag
    @blp.response(202,description="deleting tag",example={"message":"Tag Deleted"})
    @blp.alt_response(404,description="Tag not found")
    @blp.alt_response(400,description="tag assigned to one or more items")
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit
            return{"message":"deleted tag"}
        abort(400,message="could not delete tag")
