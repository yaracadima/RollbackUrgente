from pymongo import MongoClient
import certifi

MONGO_URI = "mongodb+srv://yaracadima_db_user:5nObjFeS2z52XmUM@cluster0.yoyba5k.mongodb.net"
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db=client["dbb_products_app"]
    except ConnectionError:
        print('error de conexion con la bdd')
    return db