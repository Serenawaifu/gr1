GrassFarmBot README


---

Introduction

GrassFarmBot is a Telegram bot that automates account management, proxy handling, and CAPTCHA solving for Grass Mining. It supports adding, listing, deleting accounts, managing proxies, and solving CAPTCHAs using an external API.

Supported Mining Speeds

✅ Grass Mining 1.0x
✅ Grass Mining 1.5x


---

Installation Guide

1. Install Dependencies

Ensure you have Python 3.9+ installed. Then, install the required dependencies:

pip install -r requirements.txt

2. Replace API Keys

Open main.py and replace the placeholders:

YOUR_TELEGRAM_TOKEN → Your Telegram bot token.

YOUR_CAPTCHA_API_KEY → API key for CAPTCHA solving.



3. Set Up the Database

Run the following command to initialize the database:

python -c "import aiosqlite; import asyncio; asyncio.run(aiosqlite.connect('grass.db'))"

4. Prepare Proxy File (Optional)

If using proxies, create a proxies.txt file with the following format:

email@example.com:password
socks5://user:pass@1.1.1.1:8080

5. Run the Bot

Start the bot using:

python main.py


---

Telegram Commands


---

Troubleshooting

1. Bot Not Responding

Ensure the correct Telegram token is used.

Check if the bot is added to a group or chat.



2. CAPTCHA Solving Issues

Verify the CAPTCHA API key is valid.

Make sure the captchatools library is installed.



3. Database Errors

If errors occur, try deleting grass.db and rerunning the bot.





---

License

This project is open-source and free to use. Modify and share responsibly.
