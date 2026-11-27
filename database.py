from pymongo import MongoClient
import certifi

MONGO_URI ='mongodb+srv://nayrarios_db_user:Gabr1ela0707@cluster0.47f290k.mongodb.net/'
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["dbb_products_app"]
    except ConnectionError:
        print('Error de conexión con la bdd')
    return db