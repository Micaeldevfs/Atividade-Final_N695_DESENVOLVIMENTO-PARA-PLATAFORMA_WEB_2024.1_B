from pymongo import MongoClient
from pymongo.server_api import ServerApi

# URI de conexão ao MongoDB Atlas
uri = "mongodb+srv://micael:aspirine@cluster0.cfzpz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def get_db():
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.TrabUniforplatweb
    return db