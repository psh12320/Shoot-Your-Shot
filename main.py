from telebot import *
from flask import *
from pymongo import *
import json
import time
import phonenumbers
global bot, collection


app = Flask(__name__)



def LikesLeft(user_id):
    return True



def send_message(user_id, message):
    global bot, collection
    bot.send_message(user_id, message)



def extract_liked_number(text_received):
    number = text_received.replace('/like ')



def cancel_handler(user_id):
    resetState(user_id, 0, 0, [])
    text_7 = "Your current operation was cancelled."
    send_message(user_id, text_7)




def resetState(user_id, fn_id, convo_state, meta_data):
    global collection
    collection.update_one({'telegram_user_id': {'$eq': user_id}}, {"$set": {"chat_state.fn_id": fn_id, "chat_state.convo_state": convo_state, 'chat_state.meta_data': meta_data}})



def initializeUser(user_id, message_payload, name):
    global bot, collection
    if 'contact' in message_payload:
        detected_user_id = message_payload['contact']['user_id']
        if detected_user_id == user_id:
            phone_number = message_payload['contact']['phone_number']
            user_id_state = collection.find({'_id': phone_number})
            if len(list(user_id_state)) == 0:
                collection.insert_one({
                    "_id": phone_number,
                    "telegram_user_id": user_id,
                    "chat_state":
                        {
                            "fn_id": 0,
                            "convo_state": 0,
                            "meta_data": []
                        },
                    "app_data":
                        {
                            "likes": []
                        },
                    "user_data":
                        {
                            "first_name": name,
                            "time": time.time(),
                            "registered": True,
                            "meta_data": {}
                        }
                })
                text_13 = "Congrats you have been successfully registered!"
                bot.send_message(user_id, text_13, reply_markup=types.ReplyKeyboardRemove())
                text_2 = "Use /like +65 XXXX XXXX to add the contact of your person of interest."
                send_message(user_id, text_2)
            else:
                collection.update_one({"_id": phone_number}, {"$set": {"user_data.registered": True}})   
                collection.update_one({"_id": phone_number}, {"$set": {"telegram_user_id": user_id}})   
                text_13 = "Congrats you have been successfully registered!"
                send_message(user_id, text_13, reply_markup=types.ReplyKeyboardRemove())
                number_of_likes = len(next(collection.find({'_id': phone_number}, {"app_data": 1}))['app_data']['likes'])
                text_11 = "You have already received "+str(number_of_likes)+" likes from secret admirers!"
                send_message(user_id, text_11)
                text_2 = "Use /like +65 XXXX XXXX to add the contact of your person of interest."
                send_message(user_id, text_2)
        else:
            text_1 = "Hi " + name + ", please send only YOUR number!"
            introductory_message = text_1
            keyboard = types.ReplyKeyboardMarkup (row_width = 1, resize_keyboard = True) 
            button_phone = types.KeyboardButton(text = 'Press here!', request_contact = True)
            keyboard.add(button_phone) 
            bot.send_message(user_id, introductory_message, reply_markup = keyboard)
    else:
        text_1 = "Hi " + name + ", please register your number!"
        introductory_message = text_1
        keyboard = types.ReplyKeyboardMarkup (row_width = 1, resize_keyboard = True)
        button_phone = types.KeyboardButton(text = 'Press here!', request_contact = True)
        keyboard.add(button_phone) 
        bot.send_message(user_id, introductory_message, reply_markup = keyboard)



def commandHandler(user_id, phone_number, message_payload, name, user_id_state):
    if 'text' in message_payload:
        text_received = message_payload['text']
        if '/like' in text_received:
            if LikesLeft(user_id) == False: # TODO: Likes left checker
                send_message(user_id, "Sorry, you have no more likes left.")
                return None
            number = extract_liked_number(text_received)
            if number == False: # Format is incorrect for the number entered
                pass



def MessageHandler(user_id, message_payload, name, user_id_state):
    global bot, collection
    user_id_state = list(user_id_state)
    if len(user_id_state) == 0: # Not yet registered or no one liked yet
        initializeUser(user_id, message_payload, name)
    elif user_id_state[0]['user_data']['registered'] == False: # Not yet registered but someone has liked already
        initializeUser(user_id, message_payload, name)
    else:
        user_id_state = user_id_state[0]
        phone_number = user_id_state['_id']
        if "text" in message_payload:
            if '/cancel' in message_payload['text']:
                cancel_handler(user_id)
                return None
        if user_id_state['chat_state']['fn_id'] == 0: # Check for any commands
            commandHandler(user_id, phone_number, message_payload, name, user_id_state)





@app.route("/", methods=['POST'])
def index():
    input_tele = json.loads(request.data.decode())
    if 'message' not in input_tele:
        user_id = input_tele['my_chat_member']['chat']['id']
        resetState(user_id, 0, 0, [])
        return '.'
    user_id = input_tele['message']['from']['id']
    name = input_tele['message']['from']['first_name']
    message_payload = input_tele['message']
    user_id_state = collection.find({'telegram_user_id': {'$eq': user_id}})
    MessageHandler(user_id, message_payload, name, user_id_state)
    return '.'



if __name__=="__main__":
    bot = TeleBot("5472045640:AAHahE2Pp5iheWd0H2HNsLbKDk2a5YRViKE") 
    uri = "mongodb+srv://cluster0.cvl9b.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='private/binance.pem')
    db = client['shootyoushot']
    collection = db['users']
    app.run(debug=True, host='0.0.0.0', port=5879)
