import os
import time
import logging
import requests
import telebot
from dotenv import load_dotenv
import threading

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

def get_sol_price():
    """Get the current SOL price from CoinGecko API"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "solana", "vs_currencies": "usd", "include_market_cap": "true", "include_24hr_vol": "true", "include_24hr_change": "true", "include_last_updated_at": "true", "precision": "2"
                },
            headers={"accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return data["solana"]["usd"]
    except Exception as e:
        logger.error(f"Error fetching SOL price: {e}")
        return None

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle the /start command"""
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "🚀 Welcome to the SOL Price Signal Bot! 🚀\n\n"
        "I'll send you SOL price updates every 5 minutes.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/stop - Stop receiving updates\n"
        "/price - Get current SOL price"
    )
    
    # Add chat to active chats if not already there
    if chat_id not in active_chats:
        active_chats[chat_id] = True
        print("aaaaaaa")
        logger.info(f"Started price updates for chat {chat_id}")
        # Start price updates in a separate thread
        thread = threading.Thread(target=send_price_updates, args=(chat_id,))
        thread.daemon = True
        thread.start()

@bot.message_handler(commands=['stop'])
def stop_command(message):
    """Handle the /stop command"""
    chat_id = message.chat.id
    if chat_id in active_chats:
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
    sol_price = get_sol_price()
    
    if sol_price:
        bot.send_message(
            chat_id,
            f"💰 Current SOL Price: ${sol_price:.2f} USD"
        )
    else:
        bot.send_message(
            chat_id,
            "⚠️ Sorry, I couldn't fetch the SOL price at the moment. Please try again later."
        )

def send_price_updates(chat_id):
    """Send price updates every 5 minutes."""
    prev_price = None
    
    while active_chats.get(chat_id, False):
        sol_price = get_sol_price()
        
        if sol_price:
            # Format the message with price change indicator if we have a previous price
            if prev_price:
                change = sol_price - prev_price
                change_percent = (change / prev_price) * 100
                
                if change > 0:
                    indicator = "🟢 ↗️"
                    change_text = f"+${change:.2f} (+{change_percent:.2f}%)"
                elif change < 0:
                    indicator = "🔴 ↘️"
                    change_text = f"${change:.2f} ({change_percent:.2f}%)"
                else:
                    indicator = "⚪ →"
                    change_text = "No change"
                
                message = f"{indicator} SOL Price: ${sol_price:.2f} USD\n{change_text} since last update"
            else:
                message = f"💰 SOL Price: ${sol_price:.2f} USD"
            
            try:
                bot.send_message(chat_id, message)
                prev_price = sol_price
            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")
                active_chats[chat_id] = False
        
        # Wait for 5 minutes
        time.sleep(60)  # 300 seconds = 5 minutes

def main():
    """Start the bot."""
    logger.info("Starting SOL Price Signal Bot")
    bot.infinity_polling()


if __name__ == '__main__':
    main()


