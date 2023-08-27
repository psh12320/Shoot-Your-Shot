from telebot import *
from flask import *
from pymongo import *
import json
import time
import random
global bot, collection, animal_list


app = Flask(__name__)

animal_list = [
    "Anonymous Alligator", "Anonymous Ant", "Anonymous Anteater", "Anonymous Armadillo", "Anonymous Baboon", "Anonymous Badger", "Anonymous Barracuda", "Anonymous Bat", "Anonymous Bear", "Anonymous Beaver",
    "Anonymous Bee", "Anonymous Bison", "Anonymous Blackbird", "Anonymous Boar", "Anonymous Buffalo", "Anonymous Butterfly", "Anonymous Camel", "Anonymous Capybara", "Anonymous Caribou", "Anonymous Cat",
    "Anonymous Cheetah", "Anonymous Chimpanzee", "Anonymous Cobra", "Anonymous Cockroach", "Anonymous Cougar", "Anonymous Cow", "Anonymous Coyote", "Anonymous Crab", "Anonymous Crocodile", "Anonymous Crow",
    "Anonymous Deer", "Anonymous Dingo", "Anonymous Dog", "Anonymous Dolphin", "Anonymous Donkey", "Anonymous Dragonfly", "Anonymous Duck", "Anonymous Eagle", "Anonymous Elephant", "Anonymous Falcon", "Anonymous Ferret",
    "Anonymous Finch", "Anonymous Flamingo", "Anonymous Fox", "Anonymous Frog", "Anonymous Gazelle", "Anonymous Gecko", "Anonymous Giraffe", "Anonymous Gorilla", "Anonymous Grasshopper", "Anonymous Guinea Pig",
    "Anonymous Hamster", "Anonymous Hawk", "Anonymous Hedgehog", "Anonymous Hippopotamus", "Anonymous Horse", "Anonymous Hyena", "Anonymous Iguana", "Anonymous Impala", "Anonymous Jackal", "Anonymous Jellyfish",
    "Anonymous Kangaroo", "Anonymous Koala", "Anonymous Komodo Dragon", "Anonymous Lemur", "Anonymous Leopard", "Anonymous Lion", "Anonymous Lizard", "Anonymous Lobster", "Anonymous Lynx", "Anonymous Macaw",
    "Anonymous Magpie", "Anonymous Mantis", "Anonymous Meerkat", "Anonymous Mole", "Anonymous Monkey", "Anonymous Moose", "Anonymous Mosquito", "Anonymous Mouse", "Anonymous Narwhal", "Anonymous Newt", "Anonymous Octopus",
    "Anonymous Ostrich", "Anonymous Otter", "Anonymous Owl", "Anonymous Panther", "Anonymous Parrot", "Anonymous Peacock", "Anonymous Pelican", "Anonymous Penguin", "Anonymous Pigeon", "Anonymous Platypus",
    "Anonymous Porcupine", "Anonymous Puma", "Anonymous Quokka", "Anonymous Rabbit", "Anonymous Raccoon", "Anonymous Ram", "Anonymous Rat", "Anonymous Rhinoceros", "Anonymous Salamander", "Anonymous Scorpion",
    "Anonymous Seahorse", "Anonymous Shark", "Anonymous Sheep", "Anonymous Skunk", "Anonymous Sloth", "Anonymous Snail", "Anonymous Snake", "Anonymous Spider", "Anonymous Squid", "Anonymous Squirrel", "Anonymous Starfish",
    "Anonymous Stingray", "Anonymous Stork", "Anonymous Swan", "Anonymous Tapir", "Anonymous Tarantula", "Anonymous Tasmanian Devil", "Anonymous Termite", "Anonymous Tiger", "Anonymous Toad", "Anonymous Tortoise",
    "Anonymous Toucan", "Anonymous Turkey", "Anonymous Turtle", "Anonymous Vulture", "Anonymous Wallaby", "Anonymous Walrus", "Anonymous Warthog", "Anonymous Wasp", "Anonymous Weasel", "Anonymous Whale", "Anonymous Wolf",
    "Anonymous Wolverine", "Anonymous Wombat", "Anonymous Woodpecker", "Anonymous Wren", "Anonymous Yak", "Anonymous Zebra"
]



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
    global animal_list
    if user_id_state['chat_state']['convo_state'] == 1:
        if 'contact' not in message_payload:
            send_message(user_id, 'Please send a valid phone contact!')
        else:
            if "user_id" not in message_payload['contact']:
                send_message(user_id, "Make sure you send a contact who's already on telegram and you in your phone contact.")
            else:
                crush_userid = message_payload['contact']['user_id']
                crush_name = message_payload['contact']['first_name']
                crushes_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
                crushes_ids = []
                for i in crushes_lst: crushes_ids.append(i['user_id_of_crush'])
                if crush_userid in crushes_ids:
                    resetState(user_id, 0, 0, [])
                    already_exists = crush_name + ' '+'already exists in your likes list :/ Press /add to like someone again.'
                    send_message(user_id, already_exists)
                else:
                    resetState(user_id, 0, 0, [])
                    crush_payload = list(collection.find({"_id": crush_userid}))
                    if len(crush_payload) == 0:
                        lyk_message = "🤞 We will keep it a secret and let you and "+crush_name+" know whenever they like you back 🤞\nUse /send_message to send them a message ;)"
                        crushes_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
                        animal = animal_list[random.randint(0, len(animal_list))]
                        crushes_lst.append({"user_id_of_crush": crush_userid, "time": time.time(), 'first_name': crush_name, "animal": animal})
                        send_message(user_id, lyk_message)
                        collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": crushes_lst}})
                        if collection.find_one({"_id": crush_userid}):
                            send_message(crush_userid, animal+" likes you! Press /send_message to send them a message 😜")
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
                                send_message(crush_userid, "")
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
                            lyk_message = "🤞 We will keep it a secret and let you and "+crush_name+" know whenever they like you back 🤞\nUse /send_message to send them a message ;)"
                            crushes_lst = collection.find_one({"_id": user_id}, {'app_data.crushes': 1})['app_data']['crushes']
                            animal = animal_list[random.randint(0, len(animal_list))]
                            crushes_lst.append({"user_id_of_crush": crush_userid, "time": time.time(), 'first_name': crush_name, "animal": animal})
                            collection.update_one({"_id": user_id}, {"$set": {"app_data.crushes": crushes_lst}})
                            send_message(user_id, lyk_message)
                            send_message(crush_userid, animal+" likes you! Press /send_message to send them a message 😜")
                        


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
                error_message = "Please enter a valid number which corresponds to the like you want to remove"
                send_message(user_id, error_message)

def send_messageHandler(user_id, message_payload, name, user_id_state):
    global collection
    if user_id_state['chat_state']['convo_state'] == 1:
        error_message = "Please enter a valid number instead (e.g. 2)"
        if 'text' not in  message_payload:
            send_message(user_id, error_message)
        else:
            if message_payload['text'].isdigit() == False:
                send_message(user_id, error_message)
            else:
                number = int(message_payload['text'])
                cursor = collection.find(
                    {"app_data.crushes.user_id_of_crush": user_id},
                    {"_id": 1, "app_data.crushes.animal": 1}
                )
                data_likers = {}
                for document in cursor:
                    data_likers[document['_id']] = document['app_data']['crushes'][0]['animal']
                crushes = user_id_state['app_data']['crushes']
                view_payload = ""
                counter = 1
                liker_ids = []
                liker_names = []
                for crush in crushes:
                    data_likers[crush["user_id_of_crush"]] = crush["first_name"]
                for idss in data_likers:
                    liker_ids.append(idss)
                    liker_names.append(data_likers[idss])
                    
                if number > 0 and number <= len(data_likers):
                    print(liker_names, number -1)
                    send_message(user_id, "What message would you like to send "+liker_names[number-1]+"?")
                    resetState(user_id, 3, 2, [liker_ids[number -1]])
                else:
                    error_message = "Please enter a valid number which corresponds to the like you want to remove"
                    send_message(user_id, error_message)
    elif user_id_state['chat_state']['convo_state'] == 2:
        error_message = "Please enter a text"
        if 'text' not in  message_payload:
            send_message(user_id, error_message)
        else:
            text = message_payload['text']
            idtosend = user_id_state['chat_state']['meta_data'][0]
            crushes_lst = user_id_state["app_data"]['crushes']    
            is_in = False  # Check if idtosend is the person who has been liked   
            for crush in crushes_lst:
                if crush["user_id_of_crush"] == idtosend:
                    is_in = True
                    person_name = crush["animal"]
                    break
            if is_in == True:
                send_message(idtosend, person_name+" sent you a text:\n"+text+"\nUse /send_message to reply to them!")
                resetState(user_id, 0, 0, [])
                send_message(user_id, "Your message has been sent!")
            else:
                crushes_lst = collection.find_one({"_id": idtosend})["app_data"]["crushes"]
                for i in crushes_lst:
                    if i["user_id_of_crush"] == user_id:
                        send_message(idtosend, i["first_name"]+" sent you a text:\n"+text+"\nUse /send_message to reply to them!")
                        resetState(user_id, 0, 0, [])
                        send_message(user_id, "Your message has been sent!")
                        break


            


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
            bot.send_animation(user_id, 'https://cdn.discordapp.com/attachments/628770208319930398/996796560417488946/RPReplay_Final1657724646.mp4')
        elif '/remove' in text_received:
            resetState(user_id, 2, 1, [])
            if len(user_id_state['app_data']['crushes']) == 0:
                remove_message = 'You have not liked anyone yet! Click on /add to add a like and shoot your shot 🎯'
                resetState(user_id, 0, 0, [])
                send_message(user_id, remove_message)
            else:
                resetState(user_id, 2, 2, [])
                remove_message = '\nWrite the number beside person you want to remove!'
                viewHandler(user_id, message_payload, name, user_id_state)
                send_message(user_id, remove_message)

        elif '/view' in text_received:
            if len(user_id_state['app_data']['crushes']) == 0:
                remove_message = 'You have not liked anyone yet! Click on /add to add a like and shoot your shot 🎯'
                send_message(user_id, remove_message)
            else:
                view_payload = "Here are your likes!"
                send_message(user_id, view_payload)
                viewHandler(user_id, message_payload, name, user_id_state)
        elif '/about' in text_received:
            about_message = "💓 This bot aims to help users to confess to their persons of interest in an anonymous manner.\n\n😌 We wish to help users who are shy to 'shoot' their interest without any fear of exposure or rejection.\n\n🤐 The bot keeps the confession a secret until your person of interest shoots you as well. We will then notify both persons of the match :)\n\n💡If you have any suggestions for the bot, send them in at https://forms.gle/pGeHr9AKCb6C2JoQ6. Thank you!"
            send_message(user_id, about_message)
        elif '/suggestion' in text_received:
            suggestion_message = "https://forms.gle/pGeHr9AKCb6C2JoQ6"
            send_message(user_id, suggestion_message)
        elif '/privacy' in text_received:
            privacy = "Your or your person of interest's phone number and all personally identifiable data **are not** stored in our database. We only store what's absolutely necessary for the bot to function."
            send_message(user_id, privacy)
        elif '/send_message' in text_received:
            user_id_to_find = user_id 
            cursor = collection.find(
                {"app_data.crushes.user_id_of_crush": user_id_to_find},
                {"_id": 1, "app_data.crushes.animal": 1}
            )
            data_likers = {}
            for document in cursor:
                data_likers[document['_id']] = document['app_data']['crushes'][0]['animal']
            crushes = user_id_state['app_data']['crushes']
            view_payload = ""
            counter = 1
            for crush in crushes:
                data_likers[crush["user_id_of_crush"]] = crush["first_name"]
            print(data_likers)
            if len(data_likers) == 0:
                send_message(user_id, "No one has liked you yet neither have you liked anyone yet to send a message to! Use /add to add new likes to send messages to.")
            else:
                message = "Choose the option of the person you want to send a message to: (e.g. 1):\n"
                count = 1
                for i in data_likers:
                    message = message+  str(count)+". "+str(data_likers[i])+'\n'
                    count += 1
                send_message(user_id, message)
                resetState(user_id, 3, 1, [])


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
        elif user_id_state['chat_state']['fn_id'] == 3: # Send over to /send_message handler
            send_messageHandler(user_id, message_payload, name, user_id_state)
        


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
    uri = "mongodb+srv://cluster0.mqlx5ut.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.pem')
    db = client['shootyoushot']
    collection = db['users']
    app.run(debug=True, host='0.0.0.0', port=5259)
