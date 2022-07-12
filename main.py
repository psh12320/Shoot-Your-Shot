from telebot import *
from flask import *
from pymongo import *
import json
import time
global bot, collection


app = Flask(__name__)


def send_message(user_id, message):
    global bot, collection
    bot.send_message(user_id, message)



def removeCrush(user_id, crush_userid):
    global collection
    crush_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
    updated_lst = []
    for crush in crush_lst:
        if crush['user_id_of_crush'] != crush_userid:
            updated_lst.append(crush)
    collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": updated_lst}})



def resetState(user_id, fn_id, convo_state, meta_data):
    global collection
    collection.update_one({"_id": user_id}, {"$set": {"chat_state.fn_id": fn_id, "chat_state.convo_state": convo_state, 'chat_state.meta_data': meta_data}})



def viewHandler(user_id, message_payload, name, user_id_state):
    global collection
    crushes = user_id_state['app_data']['crushes']
    view_payload = ""
    counter = 1
    for crush in crushes:
        view_payload = view_payload + str(counter) + ". "+crush['first_name']+'\n'
        counter += 1
    send_message(user_id, view_payload)


def cancelHandler(user_id):
    cancel_message = "Your current operation was cancelled. Press /add to add another contact."
    resetState(user_id, 0, 0, [])
    send_message(user_id, cancel_message)



def addHandler(user_id, message_payload, name, user_id_state):
    global collection
    if user_id_state['chat_state']['convo_state'] == 1:
        if 'contact' not in message_payload:
            send_message(user_id, 'Please send a valid phone contact!')
        else:
            if "user_id" not in message_payload['contact']:
                send_message(user_id, "Make sure you send a contact who's already on telegram and you in your phone contact.")
            else:
                crush_userid = message_payload['contact']['user_id']
                crush_name = message_payload['contact']['first_name']
                resetState(user_id, 0, 0, [])
                crush_payload = list(collection.find({"_id": crush_userid}))
                if len(crush_payload) == 0:
                    # lyk_message = "🤞 We will keep it a secret and let you know and "+ crush_name +" know whenever they likes you back 🤞"
                    lyk_message = "🤞 We'll let you know if "+crush_name+" like you back too!"
                    crushes_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
                    crushes_lst.append({"user_id_of_crush": crush_userid, "time": time.time(), 'first_name': crush_name})
                    print(crushes_lst)
                    collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": crushes_lst}})
                    send_message(user_id, lyk_message)
                else: 
                    crush_payload = crush_payload[0]
                    crushes_of_crush = crush_payload['app_data']['crushes']
                    no_match = True
                    for heartbreaks in crushes_of_crush:
                        if user_id == heartbreaks['user_id_of_crush']:
                            lyk_message = crush_name + " likes you too ❤️"
                            send_message(user_id, lyk_message)
                            message_for_crush = name + " likes you too ❤️"
                            send_message(crush_userid, message_for_crush)
                            no_match = False
                            
                            mutual_crushes_lst = collection.find_one({"_id": user_id}, {'app_data.mutual_likes': 1})['app_data']['mutual_likes']
                            mutual_crushes_lst.append({"user_id_of_crush": crush_userid, "time": time.time(), 'first_name': crush_name})
                            collection.update_one({"_id": user_id}, {"$set": {"app_data.mutual_likes": mutual_crushes_lst}})
                            removeCrush(user_id, crush_userid)

                            mutual_crushes_lst = collection.find_one({"_id": crush_userid}, {'app_data.mutual_likes': 1})['app_data']['mutual_likes']
                            mutual_crushes_lst.append({"user_id_of_crush": user_id, "time": time.time(), 'first_name': name})
                            collection.update_one({"_id": crush_userid}, {"$set": {"app_data.mutual_likes": mutual_crushes_lst}})
                            removeCrush(crush_userid, user_id)




                    if no_match == True:
                        lyk_message = "🤞 We will keep it a secret and let you know and "+ crush_name +" know whenever they likes you back 🤞"
                        crushes_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
                        crushes_lst.append({"user_id_of_crush": crush_userid, "time": time.time(), 'first_name': crush_name})
                        collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": crushes_lst}})
                        send_message(user_id, lyk_message)
                        


def removeHandler(user_id, message_payload, name, user_id_state):
    global collection
    error_message = "Please enter a valid number instead (e.g. 2)"
    if 'text' not in  message_payload:
        send_message(user_id, error_message)
    else:
        if message_payload['text'].isdigit() == False:
            send_message(user_id, error_message)
        else:
            number = int(message_payload['text'])
            crushes_list = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
            if number > 0 and number <= len(crushes_list):
                remove_message = "You have stopped liking "+crushes_list[number-1]['first_name']
                del(crushes_list[number-1])
                collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": crushes_list}})
                send_message(user_id, remove_message)
                resetState(user_id, 0, 0, [])

            else:
                error_message = "Please enter a valid number which corresponds to the crush you want to remove"
                send_message(user_id, error_message)



def commandHandler(user_id, message_payload, name, user_id_state):
    if 'text' in message_payload:
        text_received = message_payload['text']
        if '/start' in text_received:
            introductory_message = "Hi "+name+'! Use /add to add the person you are interested in!' 
            send_message(user_id, introductory_message)
            introductory_message = "To read more about this bot's methodology, press /about." 
            send_message(user_id, introductory_message)
        elif '/add' in text_received:
            resetState(user_id, 1, 1, [])
            # TODO: TEST TO SEE IF THE USER CAN ADD MORE CRUSHSES OR NOT
            add_message = "Send the contact of the person you like as shown in the video below 👇 and we'll let you know if they like you back! 😊"
            send_message(user_id, add_message)
            bot.send_document(user_id, 'https://cdn.discordapp.com/attachments/628770208319930398/993887301576970270/ezgif.com-gif-maker.gif')
        elif '/remove' in text_received:
            resetState(user_id, 2, 1, [])
            if len(user_id_state['app_data']['crushes']) == 0:
                remove_message = 'You have not liked anyone yet! Click on /add to add a crush :)'
                resetState(user_id, 0, 0, [])
                send_message(user_id, remove_message)
            else:
                resetState(user_id, 2, 2, [])
                remove_message = '\nWrite the correspoding number of the person you want to remove!'
                viewHandler(user_id, message_payload, name, user_id_state)
                send_message(user_id, remove_message)

        elif '/view' in text_received:
            if len(user_id_state['app_data']['crushes']) == 0:
                remove_message = 'You have not liked anyone yet! Click on /add to add a crush :)'
                send_message(user_id, remove_message)
            else:
                view_payload = "Here are your likes!"
                send_message(user_id, view_payload)
                viewHandler(user_id, message_payload, name, user_id_state)
        elif '/about' in text_received:
            about_message = "This bot aims to help users to confess to their persons of interest in an anonymous manner. We believe that users, who are shy but have a liking for another person, can convey their interest to them without any fear of exposure or rejection. As such, the bot will keep the confession a secret until your person of interest also sends your contact to the bot. We will then notify both of you of the match :) If you have any suggestions for our bot, send them in at https://forms.gle/pGeHr9AKCb6C2JoQ6. Thank you!"
            send_message(user_id, about_message)
        elif '/suggestion' in text_received:
            suggestion_message = "https://forms.gle/pGeHr9AKCb6C2JoQ6"
            send_message(user_id, about_message)
        elif '/privacy' in text_received:
            privacy = "Your or your liked person's phone number and all personally identifiable data **are not** stored in our database. We only store what's absolutely necessary for the bot to function."
            send_message(user_id, privacy)


def initializeUser(user_id, name):
    global bot, collection
    introductory_message = "Hi "+name+'! Use /add to add the person you are interested in!' 
    send_message(user_id, introductory_message)
    collection.insert_one({
    "_id": user_id,
    "chat_state":
        {
            "fn_id": 0,
            "convo_state": 0,
            "meta_data": []
        },
    "app_data":
        {
            "mutual_likes": [],
            "crushes": []
        },
    "user_data":
        {
            "first_name": name,
            "time": time.time(),
            "meta_data": {}
        }
    })



def MessageHandler(user_id, message_payload, name, user_id_state):
    global bot, collection
    user_id_state = list(user_id_state)
    if len(user_id_state) == 0:
        initializeUser(user_id, name)
    else:
        if "text" in message_payload:
            if '/cancel' in message_payload['text']:
                cancelHandler(user_id) 
                return None
        user_id_state = user_id_state[0]
        if user_id_state['chat_state']['fn_id'] == 0: # Check for any commands
            commandHandler(user_id, message_payload, name, user_id_state)
        elif user_id_state['chat_state']['fn_id'] == 1: # Send over /add handler
            addHandler(user_id, message_payload, name, user_id_state)
        elif user_id_state['chat_state']['fn_id'] == 2: # Send over to /remove handler
            removeHandler(user_id, message_payload, name, user_id_state)


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
    user_id_state = collection.find({'_id': user_id})
    MessageHandler(user_id, message_payload, name, user_id_state)
    return '.'



if __name__=="__main__":
    bot = TeleBot("5472045640:AAHahE2Pp5iheWd0H2HNsLbKDk2a5YRViKE") 
    uri = "mongodb+srv://cluster0.cvl9b.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='binance.pem')
    db = client['shootyoushot']
    collection = db['users']
    app.run(debug=True, host='0.0.0.0', port=443)
