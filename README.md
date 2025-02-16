<b><big><font size="+5">PriceIndicator Telegram Bot</font></big></b>

This is a Python script that runs a Telegram bot. You can use this bot to search for the average price of sold items on eBay and the current average price of items on Subito.it.

<b>Note:</b> On eBay, the average price is based only on items sold through auctions.

You can use the following commands on Telegram:

<b>/config</b>: Returns the current items listed in the configuration file (.ini) located in the folder. To add new items to the file, you need to use the main.py script.

<b>/subito</b>: Provides the average price on Subito.it for all the items you have added to the configuration file.

<b>/ebay</b>: Similar to /subito, but for eBay.

<b>/search</b>: Allows you to input the name of the items you want to search and specify any words you want to exclude from the search. The script will return the average price on both eBay and Subito.it for the specified items.
