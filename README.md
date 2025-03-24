# SOL Price Signal Bot

A Telegram bot that sends Solana (SOL) price updates every 5 minutes.

## Features

- Automatic price updates every 5 minutes
- Price change indicators (up/down/unchanged)
- Percentage and absolute price change calculations
- Manual price check command

## Setup Instructions

1. **Create a Telegram Bot**:
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Use the `/newbot` command and follow instructions
   - Copy the API token provided

2. **Configure the Bot**:
   - Create a `.env` file in the project directory
   - Add your Telegram token: `TELEGRAM_TOKEN=your_token_here`

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the Bot**:
   ```
   python sol_price_bot.py
   ```

## Commands

- `/start` - Start receiving price updates every 5 minutes
- `/stop` - Stop receiving price updates
- `/price` - Get the current SOL price immediately

## Deployment

For 24/7 operation, consider deploying to a cloud service like:
- Heroku
- AWS
- DigitalOcean
- Railway
```

## How to run the bot:

```bash
pip install -r requirements.txt
```

```bash
python sol_price_bot.py
