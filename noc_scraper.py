
import aiohttp
import asyncio
from collections import namedtuple
import requests
import os

API_URL = "http://api.newoldcamera.com/api/products"

DATA_FUJI_CAMERA = {"marca":"FUJIFILM DIGITALE",
        "tipo":"CO",
        "disponibile":"M",
        "bottega":"Usato"}

DATA_FUJI_LENS = {"marca":"FUJIFILM DIGITALE",
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

HEADERS = {"Accept":"application/json, text/javascript, */*; q=0.01",
           "Accept-Encoding":"gzip, deflate",
           "Accept-Language":"it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
           "Connection":"keep-alive",
           "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
           "Host":"api.newoldcamera.com",
           "Origin":"http://www.newoldcamera.com",
           "Referer":"http://www.newoldcamera.com/",
           "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"}

TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']
TL_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

Brand = namedtuple('Brand', ['keywords', 'data_params'])
fujifilm_cameras = Brand(['X-100', "X-E4"], DATA_FUJI_CAMERA)
ricoh_cameras = Brand(['GR'], DATA_RICOH_CAMERA)
canon_cameras = Brand(['G7X'], DATA_CANON_CAMERA)
fujifilm_lens = Brand(['27'], DATA_FUJI_LENS)

list_to_scrape =  [fujifilm_cameras, ricoh_cameras, canon_cameras, fujifilm_lens]

async def scrape(brand: Brand):
   async with aiohttp.ClientSession() as session:
      response = await session.post(url=API_URL, data=brand.data_params, headers=HEADERS)
      json_output = await response.json()
      await lookForMatch(json_output, brand)

async def lookForMatch(json, brand: Brand):
   results = json['Result']
   if results:
      for result in results:
         for keyword in brand.keywords:
            if keyword in result['modello']:
               msg = f"❗️Match❗️\n{result['modello']} | €{result['prezzovendita']} | {result['stato']} | {'Disponibile :)' if result['prenotato'] == 0 else 'Prenotato :('}\nLink: http://www.newoldcamera.com/Scheda.aspx?Codice={result['codice']}"
               sendMessageToBot(msg)
               #print(msg)

def sendMessageToBot(message):
   #start_time = time.time()
   try:
      requests.post(TL_URL, json={'chat_id': CHAT_ID, 'text': message})
      #time_diff = time.time() - start_time
      #print(f'sending time: %.3f seconds.' % time_diff)
   except Exception as e:
      print(e)

async def main():
   #start_time = time.time()
   tasks = []
   for prd in list_to_scrape:
      task = asyncio.create_task(scrape(prd))
      tasks.append(task)
   await asyncio.gather(*tasks)
   #time_diff = time.time() - start_time
   #print(f'Scraping time: %.3f seconds.' % time_diff)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
