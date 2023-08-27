from pymongo import MongoClient
uri = "mongodb+srv://cluster0.mqlx5ut.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.pem')
db = client['shootyoushot']
collection = db['users']

# Specify the user_id_of_crush you're looking for
user_id_to_find = 5226489180

# Use the find method with a query to retrieve the _id of matching documents
cursor = collection.find(
    {"app_data.crushes.user_id_of_crush": user_id_to_find},
    {"_id": 1, "app_data.crushes.animal": 1}
)

# Iterate through the cursor to access the results
data = {}
for document in cursor:
    data[document['_id']] = document['app_data']['crushes'][0]['animal']
print(data)
client.close()