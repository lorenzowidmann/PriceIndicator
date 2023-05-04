from operator import sub
import requests
from bs4 import BeautifulSoup
from platform import platform
from termcolor import colored

#Parole da rimovere per ogni ricerca
word_remove_list = ['scheda', 'ricambi', 'cover', 'protezione', 'rotto', 'batteria', 'custodia']

def average(list):
    if len(list) == 0:
        avg = 0
    else:
        avg = sum(list)/len(list)
    return avg

def out_average(list):
    outList = []
    averageValue = average(list)
    for x in list: 
        if x > averageValue/2.0: 
            if x < averageValue*1.5:
                outList.append(x)
    return outList

def is_float(list):
    floatList = []
    for x in list:
        xIsFloat = False
        try:
            float(x)
            xIsFloat = True
        except ValueError:
            xIsFloat = False

        if xIsFloat == True: 
            floatList.append(float(x))
    return floatList

def page_request_result(site_url, id_string):
    request_result=requests.get(site_url)
    soup = BeautifulSoup(request_result.text, "html.parser")
    page_top=soup.find(id=id_string)
    return page_top

def gen_word_remover(list):
    single_string = ''
    for x in list: 
        if list.index(x) != 0:
            single_string = single_string + '+' + x
        else: 
            single_string = x
    return single_string

def link_solded_items(search, search_remove, size, list = word_remove_list):
    if search_remove != '':
        complete_searche_remove = search_remove + '+' + size_differential(size) + '+' + gen_word_remover(list)
    else:
        complete_searche_remove = size_differential(size) + '+' + gen_word_remover(list)
    complete_searche = search + '+' + size
    site_url = f'https://www.ebay.it/sch/i.html?_from=R40&_nkw={complete_searche}&_in_kw=3&_ex_kw={complete_searche_remove}&_sacat=0&_udlo=&_udhi=&LH_Auction=1&_ftrt=901&_ftrv=1&_sabdlo=&_sabdhi=&_samilow=&_samihi=&_sadis=15&_stpos=39100&_sargn=-1%26saslc%3D1&_salic=101&_sop=1&_dmd=1&_ipg=60&LH_Sold=1&rt=nc'
    return site_url

def telegram_message(message):
    token = "5222921867:AAFzL-IV4o1CU8C2Ncgea3yQO3VRREtGfwo"
    chat_id = '236543289'
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()

def items_price_average(url):
    page_top = page_request_result(url,"mainContent")
    if page_top is not None:
        #finding the cost
        phone_price = page_top.find_all(class_="s-item__price")
        phone_shipping = page_top.find_all(class_="s-item__shipping s-item__logisticsCost")
    
        prices = []
        shipping = []
        i = 0 
        for info in phone_price:
            if len(phone_shipping) > i:
                if len(phone_price) > i:
                    if phone_shipping[i].getText() != 'Spedizione non specificata':
                        if str(phone_price[i]).find('ITALIC') == -1:
                                prices.append(info.getText().replace('EUR ', '').replace('.','').replace(',','.'))
            i = i + 1 

        i = 0
        for info in phone_shipping:
            if len(phone_shipping) > i:
                if len(phone_price) > i:
                    if phone_shipping[i].getText() != 'Spedizione non specificata':
                        if str(phone_price[i]).find('ITALIC') == -1:
                            shipping.append(info.getText().replace('+EUR ', '').replace(',','.').replace(' di spedizione', '').replace('Spedizione gratis', '0').replace('Spedizione non specificata','0'))
            i = i + 1
        
        average_price = average(out_average(is_float(prices)))
        average_shipping = average(out_average(is_float(shipping)))
        return average_price + average_shipping

    else: 
        #returning fake output
        fake_price = 0.00
        return fake_price

#Size differential
def size_differential(size):
    size_removal = ''
    if size == '32GB':
        size_removal = '64GB+128GB+256GB+512GB+1TB'
    elif size == '64GB':
        size_removal = '32GB+128GB+256GB+512GB+1TB'
    elif size == '128GB':
        size_removal = '32GB+64GB+256GB+512GB+1TB'
    elif size == '256GB':
        size_removal = '32GB+64GB+128GB+512GB+1TB'
    elif size == '512GB':
        size_removal = '32GB+64GB+128GB+256GB+1TB'
    return size_removal

#Media prezzi oggetti con lo stesso nome su subito 
def SUBITO_link_solded_items(search, size):
    complete_search = search + '+' + size
    site_url = f'https://www.subito.it/annunci-italia/vendita/usato/?q={complete_search}'
    return site_url

def SUBITO_price_average(url):
    request_result=requests.get(url)
    soup = BeautifulSoup(request_result.text, "html.parser")
    page_top=soup.find(id="layout" )
    phone_price = page_top.find_all(class_="index-module_price__N7M2x SmallCard-module_price__yERv7 price index-module_small__4SyUf")

    prices = []
    for info in phone_price:
        prices.append(info.getText().replace('\xa0€', '').replace('Spedizione disponibile', '').replace('.',''))
    
    average_price = average(out_average(is_float(prices)))
    return average_price

#exit handler function 
def exit_handler(text):
    print(text)