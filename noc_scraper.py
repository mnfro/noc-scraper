import aiohttp
import asyncio
from collections import namedtuple
import requests
import os
import json
import time

API_URL = "https://apinocservice.azurewebsites.net/api/products" #"http://api.newoldcamera.com/api/products"

DATA_FUJI_CAMERA = {"marca":"FUJIFILM DIGITALE",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_FUJI_CAMERA_X = {"marca":"FUJIFILM X",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_FUJI_LENS = {"marca":"FUJIFILM X",
        "tipo":"OB",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_RICOH_CAMERA = {"marca":"RICOH DIGITALE",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_CANON_CAMERA = {"marca":"CANON DIGITALE",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_YASHICA_CAMERA = {"marca":"YASHICA AF",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

HEADERS = {"Accept":"application/json, text/javascript, */*; q=0.01",
           "Accept-Encoding":"gzip, deflate",
           "Accept-Language":"it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
           "Connection":"keep-alive",
           "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
           "Host":"apinocservice.azurewebsites.net",
           "Origin":"http://www.newoldcamera.com",
           "Referer":"http://www.newoldcamera.com/",
           "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"}

TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']
TL_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

Match = namedtuple('Match', ['keywords', 'data_params'])
fujifilm_cameras = Match(['100', 'E4'], DATA_FUJI_CAMERA)
fujifilm_cameras_x = Match(['100', 'E4'], DATA_FUJI_CAMERA_X)
ricoh_cameras = Match(['GR'], DATA_RICOH_CAMERA)
yashica_cameras = Match(['T4'], DATA_YASHICA_CAMERA)
canon_cameras = Match(['G7X'], DATA_CANON_CAMERA)
fujifilm_lens = Match(['27'], DATA_FUJI_LENS)

match_list = [fujifilm_cameras_x, ricoh_cameras, yashica_cameras, canon_cameras, fujifilm_lens, fujifilm_cameras]
ignore_id_list = []

async def scrape(match: Match):
   async with aiohttp.ClientSession() as session:
      response = await session.post(url=API_URL, data=match.data_params, headers=HEADERS)
      json_output = await response.json()
      await lookForMatch(json_output, match)

async def lookForMatch(json, match: Match):
   results = json['Result']
   if results:
      for result in results:
         for keyword in match.keywords:
            if keyword in result['modello'] and result['ID'] not in ignore_id_list:
               msg = f"❗️Match❗️\n{result['modello']} | €{result['prezzovendita']} | {result['stato']} | {'Disponibile :)' if result['prenotato'] == 0 else 'Prenotato :('}\nLink: http://www.newoldcamera.com/Scheda.aspx?Codice={result['codice']}"
               sendMessageToBot(msg)
               ignore_id_list.append(result['ID'])
               print(msg) 

def sendMessageToBot(message):
   start_time = time.time()
   try:
      requests.post(TL_URL, json={'chat_id': CHAT_ID, 'text': message})
      time_diff = time.time() - start_time
      print(f'Telegram sending time: %.3f seconds.' % time_diff)
   except Exception as e:
      print(e)

async def main():
   start_time = time.time()
   global ignore_id_list
   with open('./ignore_id.txt', 'r') as f:
      ignore_id_list = json.loads(f.read())

   tasks = []
   for i in match_list:
      task = asyncio.create_task(scrape(i))
      tasks.append(task)
   await asyncio.gather(*tasks)

   with open('./ignore_id.txt', 'w') as f:
      f.write(json.dumps(ignore_id_list))
   time_diff = time.time() - start_time
   print(f'Global time: %.3f seconds.' % time_diff)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
