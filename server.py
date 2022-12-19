import asyncio
import websockets
import json
import traceback
import requests

#counter names in list to convert from name to int
counterIdentifiers = ["Chaos", "Charge", "Ember", "Heaven", "Invasion", "Protection", "Stinger", "Time", "Weakness", "Wrath", "Rose", "Emergence"]

#websocket function
async def cardSearcherSocket(websocket, path):
	print("Neos client connected.")
	async for message in websocket:
		try:
			#querying cards from a general search
			if message.startswith("[query]"):
				cardList = requests.post("https://crossuniverse.net/cardInfo", json = json.loads(message[7:])).json()
				
				for card in cardList:
					await websocket.send("[list]" + card["cardID"] + "|" + card["cardType"])
			
			#requesting detailed info about one specific card
			elif message.startswith("[details]"):
				card = requests.get("https://crossuniverse.net/cardInfo/?cardID=" + message[9:] + "&lang=en").json()
				
				#send what counters it mentions
				for counter in card["counterMentions"]:
					await websocket.send("[view][counter]" + str(counterIdentifiers.index(counter)))
				
				#send what cards it mentions
				for cardID in card["cardMentions"]:
					await websocket.send("[view][mentions]" + cardID)
				
				#send what cards it is mentioned on
				for mentioningCard in card["mentionedOn"]:
					await websocket.send("[view][mentionedOn]" + mentioningCard)
				
				#send what cards are visible on it
				for cardID in card["visibleCards"]:
					await websocket.send("[view][visible]" + cardID)
				
				#send what cards it is visible on
				for visibleOnCard in card["visibleOn"]:
					await websocket.send("[view][visibleOn]" + visibleOnCard)
		except:
			await websocket.send("[error]")
			print(traceback.format_exc())

#start websocket and listen
print("Starting websocket.")
start_server = websockets.serve(cardSearcherSocket, "", 9487)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()