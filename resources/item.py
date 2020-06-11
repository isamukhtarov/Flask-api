import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required,
                                get_jwt_claims,
                                jwt_optional,
                                get_jwt_identity,
                                fresh_jwt_required)
from models.item import ItemsModel


class Item(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("price",
                        type=float,
                        required=True,
                        help="Price field can not left blank!")

    parser.add_argument("store_id",
                        type=int,
                        required=True,
                        help="Every item need store id and it must be integer")

    @jwt_required
    def get(self, name):
        item = ItemsModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found"}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemsModel.find_by_name(name):
            return {"message": "Item with name {} already exists".format(name)}, 400
        data = self.parser.parse_args()
        if not data["store_id"]:
            return {"message": "Store id cannot be null"}, 400
        item = ItemsModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occured while insert the item"}, 500
        return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": "Admin privilege is required"}, 401
        item = ItemsModel.find_by_name(name)
        if not item:
            return {"message": "Item with name {} does not found".format(name)}, 404
        item.delete_from_db()
        return {"message": "Item deleted"}

    def put(self, name):
        data = self.parser.parse_args()
        item = ItemsModel.find_by_name(name)
        if item is None:
            item = ItemsModel(name, **data)
        else:
            item.price = data["price"]
        item.save_to_db()
        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = list(map(lambda item: item.json(), ItemsModel.query.all()))
        if user_id:
            return {"items": items}, 200
        return {"items": [item["name"] for item in items],
                "message": "More data available if you are log in"
                }, 200