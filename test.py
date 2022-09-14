from pymongo import *

uri = "mongodb+srv://cluster0.cvl9b.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='private/binance.pem')
db = client['shootyoushot']
collection = db['users']
collection.update_one({'_id': "+6590053231"}, {"$set": {"app_data.likes": [{"phone_number": "11223333", "liked_state": 1, "nick_name": None}]}})