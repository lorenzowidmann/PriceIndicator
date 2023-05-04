#Telegram BOT for items price

from datetime import datetime
from platform import platform
from datetime import datetime 
import os 
import configparser
import pytz
import sys
from termcolor import colored
import PriceIndicatorFunctions
import logging
from telegram import __version__ as TG_VER

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

#Telegram 
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
    
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

#COMANDI

#Restituisce la lista degli oggetti inseriti nel file ItemsConfiguration.ini
async def configfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = ''
    for i in searching_items:
        items = items+'\n'+i.replace('+',' ')
    
    await update.message.reply_text(items)

#Restituisce il prezzo medio dei vari oggetti venduti di recente su eBay
async def globalpriceebay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    y = 0
    message = ''
    for x in solded_items_array:
        items_name = items_type_array[y].replace('+', ' ')
        y = y + 1 
        price = PriceIndicatorFunctions.items_price_average(x)
        if price > 50.0: 
            message = message+'\n'+items_name+': '+"{:.2f}".format(price)+'€'
        else:
            message = message+'\n'+items_name+': '+'Prezzo outlayers'

    await update.message.reply_text(message)

#Restituisce il prezzo medio dei vari oggetti in vendita su subito.it
async def globalpricesubito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    y = 0
    message = ''
    for x in subito_items_array:
        items_name = items_type_array[y].replace('+', ' ')
        y = y + 1 
        price = PriceIndicatorFunctions.SUBITO_price_average(x)
        if price > 50.0:
            message = message+'\n'+items_name+': '+"{:.2f}".format(price)+'€'
        else:
            message = message+'\n'+items_name+': '+'Prezzo outlayers'

    await update.message.reply_text(message)

#Restituisce un messaggio con il prezzo dell'oggetto cercato 
ITEMS, REMOVE, ENDMESSAGE = range(3)

#Inizio funzione search
async def search(update, context):
    await update.message.reply_text("Inserisci il nome dell'oggetto che vuoi cercare")
    return ITEMS

#Parte della funzione che gestisce inomi degli oggetti 
async def get_items(update, context):
    searched_items = update.message.text
    context.user_data['searched_items'] = searched_items

    await update.message.reply_text("Inserisci le parole che vuoi rimuovere dalla ricerca")
    return  REMOVE

async def get_removed(update, context):
    search_remove = update.message.text
    context.user_data['search_remove'] = search_remove
    searched_items = context.user_data['searched_items']

    searched_items = searched_items.replace(' ','+')
    search_remove = search_remove.replace(' ','+')
    #Subito
    subito_url = PriceIndicatorFunctions.SUBITO_link_solded_items(searched_items, '')
    subito_message = PriceIndicatorFunctions.SUBITO_price_average(subito_url)
    #eBay
    ebay_url = PriceIndicatorFunctions.link_solded_items(searched_items, search_remove, '')
    ebay_message = PriceIndicatorFunctions.items_price_average(ebay_url)

    message = 'Subito: '+"{:.2f}".format(subito_message)+'€'+'\n'+'eBay: '+"{:.2f}".format(ebay_message)+'€'
    await update.message.reply_text(message)
    return ConversationHandler.END


BOT_token = '5222921867:AAFzL-IV4o1CU8C2Ncgea3yQO3VRREtGfwo'
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("config", configfile))
    application.add_handler(CommandHandler("ebay", globalpriceebay))
    application.add_handler(CommandHandler("subito", globalpricesubito))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('search', search)],
        states={
        ITEMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_items)],
        REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_removed)],
        },
    fallbacks=[]
    ))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
