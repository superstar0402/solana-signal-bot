import os
import time
import logging
import requests
import telebot
from dotenv import load_dotenv
import threading
from datetime import datetime


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Dictionary to store active chats
active_chats = {}


def get_sol_data():
    """Get the current SOL data from CoinGecko API"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "solana", 
                "vs_currencies": "usd",  
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            },
            headers={"accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "price": data["solana"]["usd"],
            "market_cap": data["solana"]["usd_market_cap"],
            "volume_24h": data["solana"]["usd_24h_vol"],
            "change_24h": data["solana"]["usd_24h_change"],
            "last_updated_at": data["solana"]["last_updated_at"]
        }
    except Exception as e:
        logger.error(f"Error fetching SOL data: {e}")
        return None


@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle the /start command"""
    chat_id = message.chat.id
   
    print("aaaaaaa")
   
    bot.send_message(
        chat_id,
        "🚀 Welcome to the SOL Price Signal Bot! 🚀\n\n"
        "I'll send you SOL price updates every minute.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/stop - Stop receiving updates\n"
        "/price - Get current SOL price and market data"
    )
    print("ccccccc")
    # Add chat to active chats if not already there
   
    if chat_id not in active_chats or active_chats[chat_id] == False:
        print("ddddddd")
        active_chats[chat_id] = True
     
        logger.info(f"Started price updates for chat {chat_id}")
        # Start price updates in a separate thread
        thread = threading.Thread(target=send_price_updates, args=(chat_id,))
        thread.daemon = True
        thread.start()


@bot.message_handler(commands=['stop'])
def stop_command(message):
    """Handle the /stop command"""
    chat_id = message.chat.id
    if chat_id in active_chats and active_chats[chat_id]:
        active_chats[chat_id] = False
        bot.send_message(
            chat_id,
            "❌ SOL price updates stopped. Use /start to resume."
        )
        print("bbbbbb")
        logger.info(f"Stopped price updates for chat {chat_id}")
    else:
        bot.send_message(
            chat_id,
            "You're not currently receiving updates."
        )


@bot.message_handler(commands=['price'])
def price_command(message):
    """Handle the /price command"""
    chat_id = message.chat.id
    sol_data = get_sol_data()
   
    if sol_data:
        # Convert timestamp to readable format
        last_updated = datetime.fromtimestamp(sol_data['last_updated_at']).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Format 24h change with appropriate indicator
        if sol_data['change_24h'] > 0:
            change_24h_text = f"🟢 +{sol_data['change_24h']:.2f}%"
        elif sol_data['change_24h'] < 0:
            change_24h_text = f"🔴 {sol_data['change_24h']:.2f}%"
        else:
            change_24h_text = f"⚪ {sol_data['change_24h']:.2f}%"
            
        bot.send_message(
            chat_id,
            f"💰 Current SOL Price: ${sol_data['price']:.2f} USD\n"
            f"📊 Market Cap: ${sol_data['market_cap']:,.2f} USD\n"
            f"📈 24h Volume: ${sol_data['volume_24h']:,.2f} USD\n"
            f"📉 24h Change: {change_24h_text}\n"
            f"🕒 Last Updated: {last_updated}"
        )
    else:
        bot.send_message(
            chat_id,
            "⚠️ Sorry, I couldn't fetch the SOL data at the moment. Please try again later."
        )


def send_price_updates(chat_id):
    """Send price updates every minute."""
    prev_data = None
   
    while active_chats.get(chat_id, False):
        sol_data = get_sol_data()
       
        if sol_data:
            # Convert timestamp to readable format
            last_updated = datetime.fromtimestamp(sol_data['last_updated_at']).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Format the message with price change indicator if we have previous data
            if prev_data:
                price_change = sol_data['price'] - prev_data['price']
                price_change_percent = (price_change / prev_data['price']) * 100
               
                market_cap_change = sol_data['market_cap'] - prev_data['market_cap']
                market_cap_change_percent = (market_cap_change / prev_data['market_cap']) * 100
                
                volume_change = sol_data['volume_24h'] - prev_data['volume_24h']
                volume_change_percent = (volume_change / prev_data['volume_24h']) * 100 if prev_data['volume_24h'] != 0 else 0
               
                # Price indicators
                if price_change > 0:
                    price_indicator = "🟢 ↗️"
                    price_change_text = f"+${price_change:.2f} (+{price_change_percent:.2f}%)"
                elif price_change < 0:
                    price_indicator = "🔴 ↘️"
                    price_change_text = f"${price_change:.2f} ({price_change_percent:.2f}%)"
                else:
                    price_indicator = "⚪ →"
                    price_change_text = "No change"
               
                # Market cap indicators
                if market_cap_change > 0:
                    market_cap_indicator = "🟢 ↗️"
                    market_cap_change_text = f"+${market_cap_change:,.2f} (+{market_cap_change_percent:.2f}%)"
                elif market_cap_change < 0:
                    market_cap_indicator = "🔴 ↘️"
                    market_cap_change_text = f"${market_cap_change:,.2f} ({market_cap_change_percent:.2f}%)"
                else:
                    market_cap_indicator = "⚪ →"
                    market_cap_change_text = "No change"
                
                # 24h change indicators
                if sol_data['change_24h'] > 0:
                    change_24h_text = f"🟢 +{sol_data['change_24h']:.2f}%"
                elif sol_data['change_24h'] < 0:
                    change_24h_text = f"🔴 {sol_data['change_24h']:.2f}%"
                else:
                    change_24h_text = f"⚪ {sol_data['change_24h']:.2f}%"
                
                # Volume indicators
                if volume_change > 0:
                    volume_indicator = "🟢 ↗️"
                    volume_change_text = f"+${volume_change:,.2f} (+{volume_change_percent:.2f}%)"
                elif volume_change < 0:
                    volume_indicator = "🔴 ↘️"
                    volume_change_text = f"${volume_change:,.2f} ({volume_change_percent:.2f}%)"
                else:
                    volume_indicator = "⚪ →"
                    volume_change_text = "No change"
               
                message = (
                    f"{price_indicator} SOL Price: ${sol_data['price']:.2f} USD\n"
                    f"{price_change_text} since last update\n\n"
                    f"{market_cap_indicator} Market Cap: ${sol_data['market_cap']:,.2f} USD\n"
                    f"{market_cap_change_text} since last update\n\n"
                    f"📈 24h Volume: ${sol_data['volume_24h']:,.2f} USD\n"
                    f"{volume_indicator} {volume_change_text} since last update\n\n"
                    f"📉 24h Change: {change_24h_text}\n"
                    f"🕒 Last Updated: {last_updated}"
                )
            else:
                # Format 24h change with appropriate indicator
                if sol_data['change_24h'] > 0:
                    change_24h_text = f"🟢 +{sol_data['change_24h']:.2f}%"
                elif sol_data['change_24h'] < 0:
                    change_24h_text = f"🔴 {sol_data['change_24h']:.2f}%"
                else:
                    change_24h_text = f"⚪ {sol_data['change_24h']:.2f}%"
                
                message = (
                    f"💰 SOL Price: ${sol_data['price']:.2f} USD\n"
                    f"📊 Market Cap: ${sol_data['market_cap']:,.2f} USD\n"
                    f"📈 24h Volume: ${sol_data['volume_24h']:,.2f} USD\n"
                    f"📉 24h Change: {change_24h_text}\n"
                    f"🕒 Last Updated: {last_updated}"
                )
           
            try:
                bot.send_message(chat_id, message)
                prev_data = sol_data
            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")
                active_chats[chat_id] = False
       
        # Wait for 1 minute
        time.sleep(60)  # 60 seconds = 1 minute


def main():
    """Start the bot."""
    logger.info("Starting SOL Price Signal Bot")
    bot.infinity_polling()


if __name__ == '__main__':
    main()
