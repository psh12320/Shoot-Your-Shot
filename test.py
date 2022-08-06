import pyrogram


ojas = pyrogram.Client("xue_en587", api_id=16480543, api_hash="5d3cffde3f291638eaa9a2b6205875ef")
ojas.start()
chat = ojas.phone_number("+919765059193")
print(chat.id)