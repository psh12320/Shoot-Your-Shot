from telebot import *
from pymongo import *
import json
import time
global bot, collection




def send_message(user_id, message):
    global bot, collection
    bot.send_message(user_id, message)



def lambda_handler(event, context):
    global bot
    global collection
    bot = TeleBot("5472045640:AAHahE2Pp5iheWd0H2HNsLbKDk2a5YRViKE") 
    uri = "mongodb+srv://cluster0.cvl9b.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='private/binance.pem')
    db = client['shootyoushot']
    collection = db['users']
    input_tele = json.loads(event['body'])
    if 'message' not in input_tele:
        user_id = input_tele['my_chat_member']['chat']['id']
        resetState(user_id, 0, 0, [])
        return '.'
    user_id = input_tele['message']['from']['id']
    name = input_tele['message']['from']['first_name']
    message_payload = input_tele['message']
    user_id_state = collection.find({'_id': user_id})
    print(user_id,  message_payload, name, user_id_state)
    MessageHandler(user_id, message_payload, name, user_id_state)
    return {
        'statusCode': 200
    }