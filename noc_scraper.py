#go to page
#scrape list of products
#match list with keyword
#if found any, report the html block to a telegram chatimport requests


import aiohttp
import asyncio
import json
from collections import namedtuple
import time
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

Product = namedtuple('Product', ['keyword', 'data'])
fuji_xpro2 = Product('X-PRO', DATA_FUJI_CAMERA)
ricoh_GR = Product('GR', DATA_RICOH_CAMERA)

list_to_scrape = [fuji_xpro2, ricoh_GR]

# async def post_request():
#     async with aiohttp.ClientSession() as session:
#         response = await session.post(url=API_URL,
#                                       data=DATA_FUJI_CAMERA,
#                                       headers=HEADERS)
#         json = await response.json()
#         #pprint.pprint(json)
#         print(len(json['Result']))

# #asyncio.run(post_request())

async def scrape(item: Product):
   async with aiohttp.ClientSession() as session:
      response = await session.post(url=API_URL, data=item.data, headers=HEADERS)
      json_output = await response.json()
      message = await lookForItem(json_output, item)
      if message:
         print(message)
         await sendMessageToBot(message)

async def lookForItem(json, item: Product):
   results = json['Result']
   if results:
      for result in results:
         if item.keyword in result['modello']:
            return f"❗️Match❗️\n{result['modello']} | €{result['prezzovendita']} | {result['stato']} | {'Disponibile :)' if result['prenotato'] == 0 else 'Prenotato :('}\nLink: http://www.newoldcamera.com/Scheda.aspx?Codice={result['codice']}"

async def sendMessageToBot(message):
   start_time = time.time()
   try:
      response = requests.post(TL_URL, json={'chat_id': CHAT_ID, 'text': message})
      time_diff = time.time() - start_time
      print(f'sending time: %.3f seconds.' % time_diff)
   except Exception as e:
      print(e)

async def main():
   start_time = time.time()
   tasks = []
   for prd in list_to_scrape:
      task = asyncio.create_task(scrape(prd))
      tasks.append(task)
   await asyncio.gather(*tasks)
   time_diff = time.time() - start_time
   print(f'Scraping time: %.3f seconds.' % time_diff)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# with open('./noc_result.json') as noc_result:
#   parsed_json = json.load(noc_result)
#   products = parsed_json['Result'] #list of products
#   for product in products:
#     #print(f"📷: {product['modello']}\n⚙️: {product['stato']}\n💶: €{product['prezzovendita']}\n")
#     if "X-T2" in product['modello']:
#        print("Found a match!")
#     else:
#        print("No match found")

# #pprint.pprint(parsed_json)


