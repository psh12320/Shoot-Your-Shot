text_dic = {
    "welcome_1":"Hi ",
    "welcome_2":", please register your number!",
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
}

def text_response(i,params = None): #welcome has name inside so params = {"name": name}
    if params == None:
        return text_dic[i]
    else:
        if i=="welcome":
            return f"{text_dic['welcome_1']}{params['name']}{text_dic['welcome_2']}"
        if i=="nick_like":
            return f"{params['nickname']}{text_dic['nick_like']}"
        if i=="removed_like":
            return f"{params['button']}{text_dic['removed_like']}"
        if i=="received_like":
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

print(text_response("cancel"))
print(text_response("welcome",{"name":"vasanth"}))
print(text_response("nick_like",{'nickname':"bobehe"}))
print(text_response("removed_like",{'button':"bobehe"}))
print(text_response("received_like",{'like_count':5}))
print(text_response("nick_like",{'nickname':"bobehe"}))
print(text_response("display_like",{"likes_state":[{"liked_state":0,"nick_name":"bobb"},{"liked_state":2,"nick_name":"tabb"},{"liked_state":0,"nick_name":"sabb"},{"liked_state":2,"nick_name":"tom"},{"liked_state":0,"nick_name":"codd"},{"liked_state":0,"nick_name":"mopbb"}]}))