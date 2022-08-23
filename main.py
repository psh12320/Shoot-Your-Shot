from gc import collect
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
    try:
        parsed_number = phonenumbers.parse(text_received, None)
    except:
        print(text_received)
        return False
    if phonenumbers.is_valid_number(parsed_number):
        return parsed_number
    return False



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
            if "+" not in phone_number:
                phone_number = "+" + str(phone_number)
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



def addHandler(user_id, message_payload, name, user_id_state):
    global collection, bot
    if user_id_state['chat_state']['convo_state'] == 1:
        message_payload = message_payload['message']
        if 'text' not in message_payload:
            send_message('Please sent the text of the nickname only!')
            return None
        else:
            if len(str(message_payload['text'])) > 16:
                send_message(user_id, 'Please keep the name short and sweet :) (aka less than 16 characters).')
                return None
        meta_data = user_id_state["chat_state"]["meta_data"]
        meta_data.append(message_payload['text'])
        resetState(user_id, 1, 2, meta_data)  
        confirmation = "Kindly press the button below to confirm the details of your like:\nPhone Number: "+str(meta_data[0])+"\nNickname: "+meta_data[1]
        button_Confirm = types.InlineKeyboardButton('Confirm!', callback_data='Confirm')
        button_ReEnter = types.InlineKeyboardButton('Re-enter!', callback_data='Re-enter')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_Confirm)
        keyboard.add(button_ReEnter)
        bot.send_message(user_id, confirmation, reply_markup=keyboard)
    if user_id_state['chat_state']['convo_state'] == 2:
        if 'reply_markup' not in message_payload['message']:
            send_message(user_id, "Please press either of the buttons on the top or press /cancel to cancel current operation.")
        else:
            button_of_choice = message_payload['data']
            if button_of_choice == 'Re-enter':
                send_message(user_id, "Kindly re-enter the person you like.")
                resetState(user_id, 0, 0, [])
                return '.'
            meta_data = user_id_state['chat_state']['meta_data']
            likes_states = user_id_state['app_data']['likes']
            # Either it's about to be a mutual like or a first time like
            



def commandHandler(user_id, phone_number, message_payload, name, user_id_state):
    if 'text' in message_payload:
        text_received = message_payload['text']
        if '/like' in text_received:
            if LikesLeft(user_id) == False: # TODO: Likes left checker
                send_message(user_id, "Sorry, you have no more likes left.")
                return None
            number = text_received
            if extract_liked_number(number) == False: # Format is incorrect for the number entered
                send_message(user_id, "Please re-enter the number of the person you like in the proper format!\n Use '/like +65 XXXX XXXX' to add the contact of your person of interest.")
                return None
            number = extract_liked_number(number)
            final_number = "+"+str(number.country_code)+str(number.national_number)
            likes_states = user_id_state['app_data']['likes']
            final_number_in_likes_states = False
            index = 0
            for likes in likes_states:
                if likes['phone_number'] == final_number:
                    final_number_in_likes_states = True
                    index += 1
            if final_number_in_likes_states == True: # Not the first relation between these 2 accounts
                relation_state = likes_states[index]
                if relation_state['liked_state'] == 0 or relation_state['liked_state'] == 2:
                    send_message(user_id, "You have already previously liked this person!")
                    return None
                text_16 = "Enter the nickname of the person you like!"
                send_message(user_id, text_16) 
                resetState(user_id, 1, 1, [final_number])
            else: # First relation between these 2 account 
                text_16 = "Enter the nickname of the person you like!"
                send_message(user_id, text_16) 
                resetState(user_id, 1, 1, [final_number])



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
        elif user_id_state['chat_state']['fn_id'] == 1: # Send over /add handler
            addHandler(user_id, message_payload, name, user_id_state)



@app.route("/", methods=['POST'])
def index():
    input_tele = json.loads(request.data.decode())
    if 'message' not in input_tele and 'my_chat_member' in input_tele:
        user_id = input_tele['my_chat_member']['chat']['id']
        resetState(user_id, 0, 0, [])
        return '.'
    elif 'message' in input_tele:
        user_id = input_tele['message']['from']['id']
        name = input_tele['message']['from']['first_name']
        message_payload = input_tele['message']
        user_id_state = collection.find({'telegram_user_id': {'$eq': user_id}})
        MessageHandler(user_id, message_payload, name, user_id_state)
        return '.'
    else:
        user_id = input_tele['callback_query']['message']['chat']['id']    
        name = input_tele['callback_query']['message']['chat']['first_name']
        message_payload = input_tele['callback_query']
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
