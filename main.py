from telebot import *
from flask import *
from pymongo import *
import json
import time
import phonenumbers
global bot, collection


app = Flask(__name__)

text_dic = {
    "welcome_1":"Hi ",
    "welcome_2":", please register your number!",
    "wrong_number_1":"Hi ",
    "wrong_number_2":", please send only YOUR number!",
    "ask_like":"Use /like +65 XXXX XXXX to add the contact of your person of interest.",
    "assure_secret":"We’ll keep it a secret 🤫…and let the both of you know when you have liked each other!",
    "nick_like":" likes you too! ❤️",
    "no_likes":"You have not liked anyone yet. Use /like to send a contact or username",
    "removed_like":" was removed from your list of likes.",# needs a param={"button": button_name}
    "received_like_1":"You have already received ",
    "received_like_2":" likes from secret admirers!",
    "cancel":"You are back in main menu",
    "someone_liked":"Someone likes you! Use /like to find out who!",
    "registered":"Congrats you have been successfully registered!",
    "enter_nick":"Enter the nickname of the person you like!",
    "max_char":"Please keep the name short and sweet, less than 16 characters.",
    "only_nick":'Please send the text of the nickname only!',
    "like_confirmation_1":"Kindly press the button below to confirm the details of your like:\nPhone Number: ",
    "like_confirmation_2":"\nNickname: ",
    "button_or_cancel":"Please press either of the buttons on the top or press /cancel to cancel current operation.",
    
}

def text_response(i,params = None): #welcome has name inside so params = {"name": name}
    if params == None:
        return text_dic[i]
    else:
        if i=="welcome":
            return f"{text_dic['welcome_1']}{params['name']}{text_dic['welcome_2']}"
        if i=="wrong_number":
            return f"{text_dic['wrong_number_1']}{params['name']}{text_dic['wrong_number_2']}"
        if i=="nick_like":
            return f"{params['nickname']}{text_dic['nick_like']}"
        if i=="removed_like":
            return f"{params['button']}{text_dic['removed_like']}"
        if i=="received_like":#{"like_count": likecount}
            return f"{text_dic['received_like_1']}{params['like_count']}{text_dic['received_like_2']}"
        if i=="display_like":
            string_out = ""
            likes_state = params["likes_state"]
            liked = []
            mutual_liked = []
            for like in likes_state:
                if like['liked_state'] == 0: # Mutual like
                    mutual_liked.append(like['nick_name'])
                elif like['liked_state'] == 2: # Simple like
                    liked.append(like['nick_name'])
            if len(liked) != 0:
                string_out += "You have liked:\n"
                for index,name in enumerate(liked):
                    string_out += f"{index+1}. {name}\n"
                string_out +=  "\n"*3
            if len(mutual_liked) != 0:
                string_out += "Mutual likes:\n"
                for index,name in enumerate(mutual_liked):
                    string_out += f"{index+1}. {name}\n"
            
            return string_out
        if i=="like_confirmation":#params = {"phone":phone,"nickname":name}
            return f"{text_dic['like_confirmation_1']}{params['phone']}{text_dic['like_confirmation_2']}{params['nickname']}"

def register_number(phone_number):
    global collection
    if len(list(collection.find({"_id": phone_number}))) == 0:
        collection.insert_one({
                    "_id": phone_number,
                    "telegram_user_id": None,
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
                            "first_name": None,
                            "time": time.time(),
                            "registered": False,
                            "meta_data": {}
                        }
                })
        return False
    return True

def LikesLeft(user_id):
    return True

def send_message(user_id, message):
    global bot, collection
    bot.send_message(user_id, message)

def delete_message(message_payload):
    print("delete has been called")
    global bot, collection
    bot.delete_message(message_payload["from"]["id"], int(message_payload["message"]["message_id"])) #this has to have the chat id of the bot itself which I don't have currently so please change the userid of the bot

def extract_liked_number(text_received):
    try:
        parsed_number = phonenumbers.parse(text_received, None)
    except:
        if "+" not in text_received:
            return 0
        return 1
    if phonenumbers.is_valid_number(parsed_number):
        return parsed_number
    return 1

def cancel_handler(user_id):
    resetState(user_id, 0, 0, [])
    send_message(user_id, text_dic["cancel"])

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
                print("should be registered: ",text_response("registered"))
                bot.send_message(user_id, text_response("registered"), reply_markup=types.ReplyKeyboardRemove())
                print("should be ask_like: ",text_response("registered"))
                send_message(user_id, text_response("ask_like"))
            else:
                collection.update_one({"_id": phone_number}, {"$set": {"user_data.registered": True}})   
                collection.update_one({"_id": phone_number}, {"$set": {"telegram_user_id": user_id}})   
                print("should be registered: ",text_response("registered"))
                bot.send_message(user_id, text_response("registered"), reply_markup=types.ReplyKeyboardRemove())
                number_of_likes = len(next(collection.find({'_id': phone_number}, {"app_data": 1}))['app_data']['likes'])
                send_message(user_id, text_response("received_like",{"like_count": number_of_likes}))
                print("should be ask_like: ",text_response("registered"))
                send_message(user_id, text_response("ask_like"))
        else:
            keyboard = types.ReplyKeyboardMarkup (row_width = 1, resize_keyboard = True) 
            button_phone = types.KeyboardButton(text = 'Press here!', request_contact = True)
            keyboard.add(button_phone) 
            bot.send_message(user_id, text_response("wrong_number",{"name":name}) , reply_markup = keyboard)
    else:
        print("should be welcome: ",text_response("welcome",{"name":name}))

        keyboard = types.ReplyKeyboardMarkup (row_width = 1, resize_keyboard = True)
        button_phone = types.KeyboardButton(text = 'Press here!', request_contact = True)
        keyboard.add(button_phone) 
        bot.send_message(user_id, text_response("welcome",{"name":name}), reply_markup = keyboard)



def addHandler(user_id, message_payload, name, user_id_state):
    global collection, bot
    if user_id_state['chat_state']['convo_state'] == 1:
        #message_payload = message_payload['message']
        if 'text' not in message_payload:
            send_message(user_id,text_response("only_nick"))
            return None
        else:
            if len(str(message_payload['text'])) > 16:
                send_message(user_id, text_response("max_char"))
                return None
        meta_data = user_id_state["chat_state"]["meta_data"]
        meta_data.append(message_payload['text'])
        resetState(user_id, 1, 2, meta_data)  
        # confirmation = "Kindly press the button below to confirm the details of your like:\nPhone Number: "+str(meta_data[0])+"\nNickname: "+meta_data[1]
        button_Confirm = types.InlineKeyboardButton('Confirm!', callback_data='Confirm')
        button_ReEnter = types.InlineKeyboardButton('Re-enter!', callback_data='Re-enter')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_Confirm)
        keyboard.add(button_ReEnter)
        bot.send_message(user_id, text_response("like_confirmation",{"phone":str(meta_data[0]),"nickname":meta_data[1]}), reply_markup=keyboard)
    if user_id_state['chat_state']['convo_state'] == 2:
        if 'message' not in message_payload:
            send_message(user_id, text_response("button_or_cancel"))
        else:
            # bot.send_message(user_id, "ok", reply_markup=None)
            button_of_choice = message_payload['data']
            delete_message(message_payload)
            if button_of_choice == 'Re-enter':
                send_message(user_id, "Kindly re-enter the person you like.")
                resetState(user_id, 0, 0, [])
                return '.'
            meta_data = user_id_state['chat_state']['meta_data']
            likes_states = user_id_state['app_data']['likes']
            # Either it's about to be a mutual like or a first time like
            to_add_phone_number = meta_data[0]
            to_add_nickname = meta_data[1]
            too_add_number_in_likes_states = False
            index = 0
            for likes in likes_states:
                if likes['phone_number'] == to_add_phone_number:
                    too_add_number_in_likes_states = True
                    break
                index += 1
            if too_add_number_in_likes_states == True: # Mutual like
                likes_states[index]['nick_name'] = to_add_nickname
                likes_states[index]['liked_state'] = 0
                liked_person_liked_state = next(collection.find({"_id": to_add_phone_number}))['app_data']['likes']
                index = 0
                for like in liked_person_liked_state: 
                    if like['phone_number'] == user_id_state['_id']:
                        break 
                    index += 1
                liked_person_liked_state[index]['liked_state'] = 0
                collection.update_one({'telegram_user_id': {'$eq': user_id}}, {"$set": {"app_data.likes": likes_states}})
                collection.update_one({'_id': to_add_phone_number}, {"$set": {"app_data.likes": liked_person_liked_state}})
                send_message(user_id, text_response("nick_like",{"nickname":to_add_nickname}))
                liked_person_userid_state = next(collection.find({"_id": to_add_phone_number}))
                send_message(liked_person_userid_state['telegram_user_id'], text_response("nick_like",{"nickname":liked_person_liked_state[index]['nick_name']}))
                resetState(user_id, 0, 0, [])
            else: # First time liking
                likes_states.append({"phone_number": to_add_phone_number, "liked_state": 2, "nick_name": to_add_nickname})
                registered_already = register_number(to_add_phone_number) # If number hasn't been registered yet, it will return False
                collection.update_one({'telegram_user_id': {'$eq': user_id}}, {"$set": {"app_data.likes": likes_states}})
                if registered_already == False: # Hasn't been registered yet
                    collection.update_one({'_id': to_add_phone_number}, {"$set": {"app_data.likes": [{"phone_number": user_id_state["_id"], "liked_state": 1, "nick_name": None}]}})
                else: # Registered already
                    liked_person_liked_state = next(collection.find({"_id": to_add_phone_number}))['app_data']['likes']
                    liked_person_liked_state.append({"phone_number": user_id_state["_id"], "liked_state": 1, "nick_name": None})
                    collection.update_one({'_id': to_add_phone_number}, {"$set": {"app_data.likes": liked_person_liked_state}})
                send_message(user_id, text_response("assure_secret"))
                liked_person_userid_state = next(collection.find({"_id": to_add_phone_number}))  # TODO: INEFFICIENY 
                if liked_person_userid_state['user_data']['registered']:
                    send_message(liked_person_userid_state['telegram_user_id'], text_response("someone_liked"))
                resetState(user_id, 0, 0, []) 
                return '.'
                


def removeHandler(user_id, message_payload, name, user_id_state):
    global collection, bot
    if user_id_state['chat_state']['convo_state'] == 1:
        if 'message' not in message_payload:
            send_message(user_id, "Please press either of the buttons on the top or press /cancel to cancel current operation.")
        else:
            delete_message(message_payload)
            button_of_choice = message_payload['data']
            send_message(user_id, text_response("removed_like",{"button":button_of_choice}))
            likes_state = user_id_state['app_data']['likes']
            index = 0
            for like in likes_state:
                if like['nick_name'] == button_of_choice:
                    break
                index += 1
            liked_person_state = next(collection.find({"_id": likes_state[index]['phone_number']}))
            liked_person_liked_state = liked_person_state['app_data']['likes']
            i = 0
            for like in liked_person_liked_state:
                if like['phone_number'] == user_id_state['_id']:
                    break
                i += 1
            if likes_state[index]['liked_state'] == 0: # Mutual like
                liked_person_liked_state[i]['liked_state'] = 2
                likes_state[i]['liked_state'] = 1
            else: # Direct like
                del liked_person_liked_state[i]
                del likes_state[index]
            collection.update_one({'telegram_user_id': {'$eq': user_id}}, {"$set": {"app_data.likes": likes_state}})
            collection.update_one({'_id': liked_person_state['_id']}, {"$set": {"app_data.likes": liked_person_liked_state}})
            confirmation = "Do you want to remove more?"
            button_Confirm = types.InlineKeyboardButton('Yes', callback_data='Yes')
            button_ReEnter = types.InlineKeyboardButton('No', callback_data='No')
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_Confirm)
            keyboard.add(button_ReEnter)
            bot.send_message(user_id, confirmation, reply_markup=keyboard)
            resetState(user_id, 2, 2, [])
    elif user_id_state['chat_state']['convo_state'] == 2:
        if 'message' not in message_payload:
            send_message(user_id, "Please press either of the buttons on the top or press /cancel to cancel current operation.")
        else:
            button_of_choice = message_payload['data']
            delete_message(message_payload)

            if button_of_choice == 'No':
                send_message(user_id, 'Alright! Use /like to like someone else')
                resetState(user_id, 0, 0, [])
            elif button_of_choice == 'Yes':
                likes_state = user_id_state["app_data"]['likes']
                liked = []
                for like in likes_state:
                    if like['liked_state'] == 0 or like['liked_state'] == 2:
                        liked.append(like['nick_name'])
                if len(liked) == 0:
                    resetState(user_id, 0, 0, [])
                    delete_message(message_payload)
                    
                    send_message(user_id, text_response("no_likes"))
                    return '.'
                keyboard = types.InlineKeyboardMarkup()
                duo_liked = []
                index = 1
                if len(liked) == 1:
                    keyboard.add(types.InlineKeyboardButton(liked[0], callback_data=liked[0]))
                else: 
                    for like in liked:
                        if index != len(liked):
                            duo_liked.append([types.InlineKeyboardButton(like, callback_data=like), types.InlineKeyboardButton(liked[index], callback_data=liked[index])])
                            index += 2
                        else:
                            duo_liked.append([types.InlineKeyboardButton(like, callback_data=like)])
                    for i in duo_liked:
                        if len(i) == 2:
                            keyboard.row(i[0], i[1])
                        else:
                            keyboard.row(i[0])
                bot.send_message(user_id, "Select the name of person you wish to remove from likes: ", reply_markup=keyboard)
                resetState(user_id, 2, 1, [])



def commandHandler(user_id, phone_number, message_payload, name, user_id_state):
    global bot
    if 'text' in message_payload:
        text_received = message_payload['text']
        if '/like' in text_received:
            if LikesLeft(user_id) == False: # TODO: Likes left checker
                send_message(user_id, "Sorry, you have no more likes left.")
                return None
            number = text_received
            if extract_liked_number(number) == 0: # No areacode 
                send_message(user_id, "Please include area code in the phone number")
                return None
            if extract_liked_number(number) == 1: # Format is incorrect for the number entered
                send_message(user_id, "Please re-enter the number of the person you like in the proper format!\n Use '/like +65 XXXX XXXX' to add the contact of your person of interest.")
                return None
            number = extract_liked_number(number)
            final_number = f"+{str(number.country_code)} {str(number.national_number)}"
            likes_states = user_id_state['app_data']['likes']
            final_number_in_likes_states = False
            index = 0
            for likes in likes_states:
                if likes['phone_number'] == final_number:
                    final_number_in_likes_states = True
                    break
                index += 1
            if final_number_in_likes_states == True: # Not the first relation between these 2 accounts
                relation_state = likes_states[index]
                if relation_state['liked_state'] == 0 or relation_state['liked_state'] == 2:
                    send_message(user_id, "You have already previously liked this person!")
                    return None
                send_message(user_id, text_response("enter_nick")) 
                resetState(user_id, 1, 1, [final_number])
            else: # First relation between these 2 account 
                send_message(user_id, text_response("enter_nick")) 
                resetState(user_id, 1, 1, [final_number])
        elif '/view' in text_received:
            resetState(user_id, 0, 0, [])
            if len(user_id_state["app_data"]['likes']) == 0:
                send_message(user_id, text_response("no_likes"))
                return '.'
            
            
            

            send_message(user_id, text_response("display_like",{"likes_state":user_id_state["app_data"]['likes']}))
        elif '/remove' in text_received:
            likes_state = user_id_state["app_data"]['likes']
            liked = []
            for like in likes_state:
                if like['liked_state'] == 0 or like['liked_state'] == 2:
                    liked.append(like['nick_name'])
            if len(liked) == 0:
                send_message(user_id, text_response("no_likes"))
                resetState(user_id, 0, 0, [])
                return '.'
            keyboard = types.InlineKeyboardMarkup()
            duo_liked = []
            if len(liked) == 1:
                keyboard.add(types.InlineKeyboardButton(liked[0], callback_data=liked[0]))
            elif len(liked)%2 == 0:
                index = 0
                while index != len(liked):
                    duo_liked.append([types.InlineKeyboardButton(liked[index], callback_data=liked[index]), types.InlineKeyboardButton(liked[index+1], callback_data=liked[index+1])])
                    index += 2
            else:
                duo_liked.append([types.InlineKeyboardButton(liked[0], callback_data=liked[0])])
                del liked[0]
                index = 0
                while index != len(liked):
                    duo_liked.append([types.InlineKeyboardButton(liked[index], callback_data=liked[index]), types.InlineKeyboardButton(liked[index+1], callback_data=liked[index+1])])
                    index += 2
            for i in duo_liked:
                if len(i) == 2:
                    keyboard.row(i[0], i[1])
                else:
                    keyboard.row(i[0])
            bot.send_message(user_id, "Select the name of person you wish to remove from likes: ", reply_markup=keyboard)
            resetState(user_id, 2, 1, [])
        elif '/privacy' in text_received:
            privacy = "The only identifiable information we have on you is your **phone number** 📞\nThe data is stored with military grade encryption and no one can access it."
            send_message(user_id, privacy)
        elif '/about' in text_received:
            about = "💓 This bot helps you anonymously confess to the person you like!\n\n😌 We wish to help users who are shy to 'shoot' their interest without any fear of exposure or rejection.\n\n🤐 The bot keeps the confession a secret until your person of interest shoots you as well. We will then notify both persons of the match :)"
            send_message(user_id, about)


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
        elif user_id_state['chat_state']['fn_id'] == 2: # Send over /remove handler
            removeHandler(user_id, message_payload, name, user_id_state)
    return '.'



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
