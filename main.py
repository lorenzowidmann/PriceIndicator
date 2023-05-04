#This program find the average price of selled items on eBay and Subito.it

from datetime import datetime
from platform import platform
import PriceIndicatorFunctions
import time 
from datetime import datetime 
import os 
import configparser
import pytz
import sys
from termcolor import colored
import atexit

#Find the current os 
path = ''
if sys.platform.startswith('linux'):
    #linux
    path = '/home/ubuntu/PriceIndicator'
if sys.platform == 'win32':
    #windows
    path = 'C:\\Users\\loren\\Desktop\\PriceIndicator'

def current_time():
    now = datetime.now(pytz.timezone('Europe/Rome'))
    current_time = now.strftime("%H:%M:%S")
    return current_time

searching_items = []
config = configparser.ConfigParser()
#Tryng the path and add the items to a list
try:
    config.read(os.path.join(path,'ItemsConfiguration.ini'))
    ITEMS = {}
    for key in config['ITEMS']:
        value = config.get("ITEMS", key)
        if key[0:3] == 'typ':
            ITEMS[key] = value 
            searching_items.append(value)
        if key[0:3] == 'sol':
            ITEMS[key] = value.replace('%','%%') 
        if key[0:3] == 'sub':
            ITEMS[key] = value.replace('%','%%') 
except: 
    print(colored('Edit the path', 'red'))
    sys.exit()

#Current search
risposta_ricerche = input('Ricerche in corso: (y)').lower()
if risposta_ricerche == 'y':
    for i in searching_items:
        print(i.replace('+',' '))

search_int = input('Vuoi inserire altri oggetti: (y)').lower()
if search_int == 'y':
    print('Procedi con inserire la ricerca che vuoi efettuare')
    i = True 
    while i == True:
        items_name = input("Nome dell'oggetto: ").replace(' ','+')
        #finding if the items already exist 
        items_already_exist = False
        for x in config['ITEMS']:
            if x.lower().find(items_name.lower()) != -1: 
                print(colored('Ricerca già inserita', 'red'))
                items_already_exist = True
                break
        if items_already_exist == False:
            search_remove = input('Parole da rimuovere: ').replace(' ','+')
            size_question = input('Vuoi differenziare la memoria: (y)')
            if size_question == 'y':
                x = 1
                while x <= 5:
                    if x == 1: 
                        size = '32GB'
                    elif x == 2: 
                        size = '64GB'
                    elif x == 3: 
                        size = '128GB'
                    elif x == 4: 
                        size = '256GB'
                    elif x == 5:
                        size = '512GB'
                        
                    #setting up links and name
                    ITEMS['type_'+items_name+'_'+size] = items_name + '+' + size
                    ITEMS['solded_link_'+items_name+'_'+size] = PriceIndicatorFunctions.link_solded_items(items_name, search_remove, size).replace('%','%%')
                    ITEMS['subito_link_'+items_name+'_'+size] = PriceIndicatorFunctions.SUBITO_link_solded_items(items_name, size).replace('%','%%')
                    x = x + 1 

            else:
                #setting up links and name 
                ITEMS['type_'+items_name] = items_name
                ITEMS['solded_link_'+items_name] = PriceIndicatorFunctions.link_solded_items(items_name, search_remove, size='').replace('%','%%')
                ITEMS['subito_link_'+items_name] = PriceIndicatorFunctions.SUBITO_link_solded_items(items_name, size='').replace('%','%%')

            risposta = ''
            while risposta != 'y' or risposta!= 'n':
                risposta = input('Vuoi inserire un altro oggetto? (y/n): ').lower()
                if risposta == 'n':
                    i = False
                    break
                if risposta == 'y':
                    print('Procedi con inserire i dati richiesti')
                    break
                else:
                    print('Rispondi solamente y o n')
    
    config['ITEMS'] = ITEMS
    #Saving items
    with open(os.path.join(path,'ItemsConfiguration.ini'), 'w') as phone_link:
        config.write(phone_link)
    print(colored('CONFIGURATION DONE','green'))

#Starting the search
#converting dictionary to array 
items_type_array = []
solded_items_array = [] 
subito_items_array = []
for x in config['ITEMS']:
    value = config.get("ITEMS", x)
    if x[0:3] == 'typ':
        items_type_array.append(value)
    if x[0:3] == 'sol':
        solded_items_array.append(value.replace('%%','%'))
    if x[0:3] == 'sub':
        subito_items_array.append(value.replace('%%','%'))

risposta_starter = input('Vuoi ricevere le quotazioni complessive: (y)')
if risposta_starter == 'y':
    y = 0
    for x in solded_items_array:
        items_name = items_type_array[y].replace('+', ' ')
        print(items_name)
        y = y + 1 

        price = PriceIndicatorFunctions.items_price_average(x)
        if price > 50.0: 
            print("{:.2f}".format(price) + "€")
            PriceIndicatorFunctions.telegram_message(items_name+': '+"{:.2f}".format(price)+'€')
        else:
            print('Prezzo considerato outlayers')

single_items_search_starter = input('Vuoi cercare un oggetto nello specifico: (y)')
if single_items_search_starter == 'y':
    searched_items = input('Oggetto che stai cercando: ').replace(' ', '+').lower()
    y = 0 
    items_founded = False 
    for x in items_type_array:
        if searched_items == x.lower(): 
            price = PriceIndicatorFunctions.items_price_average(solded_items_array[y])
            print("{:.2f}".format(price) + "€")
            items_founded = True 
        y = y + 1 
    
    if items_founded == False: 
        print('Oggetto non trovato') 

text = 'PriceIndicator is closing'
atexit.register(PriceIndicatorFunctions.exit_handler, text)