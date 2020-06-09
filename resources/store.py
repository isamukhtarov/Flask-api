from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "Store with name {} does ot found".format(name)}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"message": "Store with name {} already exists".format(name)}, 400
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occured while save store to db"}, 500
        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if not store:
            return {"message": "Store with name {} doe not find".format(name)}, 404
        store.delete_from_db()
        return {"message": "Store deleted"}, 200


class StoreList(Resource):
    def get(self):
        return {"stores": list(map(lambda x: x.json(), StoreModel.query.all()))}, 200
