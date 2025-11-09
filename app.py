from flask import Flask, jsonify
from pymongo import MongoClient
from bson import ObjectId
import config.settings as settings

app = Flask(__name__)

# Mongo client/global DB handle
mongo_client = MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

def serialize_doc(doc):
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    return doc


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/api/multi_match_bonus', methods=['GET'])
def get_multi_match_bonus():
    # Collection for multi_match_bonus (dynamic routing now respected)
    results = mongo_db["multi_match_bonus"].find({}).sort("created_at", -1)
    # Protect against large results: force materialization and serialization
    docs = [serialize_doc(d) for d in results]
    return jsonify(docs)


if __name__ == '__main__':
    app.run()
