import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from loguru import logger
from database import Database
from proxy_manager import ProxyManager
from account_manager import AccountManager
from captcha_solver import CaptchaSolver
from datetime import datetime

class GrassFarmBot:
    def __init__(self):
        self.db = Database()
        self.proxy_manager = ProxyManager(self.db)
        self.captcha_solver = CaptchaSolver("YOUR_CAPTCHA_API_KEY")  # <button class="citation-flag" data-index="7"><button class="citation-flag" data-index="8">
        self.account_manager = AccountManager(
            self.db, 
            self.proxy_manager, 
            self.captcha_solver
        )
        self.telegram_app = ApplicationBuilder().token("YOUR_TELEGRAM_TOKEN").build()

    async def start(self):
        await self.db.initialize()  # Initialize DB <button class="citation-flag" data-index="5">
        await self.telegram_app.initialize()
        await self.telegram_app.start()
        await self.register_handlers()
        await self.telegram_app.updater.start_polling()
        logger.info(f"Bot started at {datetime.now()}")

    async def register_handlers(self):
        self.telegram_app.add_handler(CommandHandler("menu", self.menu))
        self.telegram_app.add_handler(CommandHandler("add_account", self.add_account))
        self.telegram_app.add_handler(CommandHandler("accounts", self.list_accounts))
        self.telegram_app.add_handler(CommandHandler("profile", self.profile))
        self.telegram_app.add_handler(CommandHandler("delete_account", self.delete_account))
        self.telegram_app.add_handler(CommandHandler("add_proxy", self.add_proxy))

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Menu:\n"
            "/add_account - Add new account\n"
            "/accounts - List your accounts\n"
            "/profile - View account details\n"
            "/delete_account - Delete account\n"
            "/add_proxy - Add proxies\n"
        )

    async def add_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        args = " ".join(context.args).strip()
        if not args:
            await update.message.reply_text("Please provide account details (email:password or email:ref:password)")
            return
        await self.account_manager.add_account_from_input(
            user_id, args, update
        )
        await update.message.reply_text("Processing account...")

    async def list_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        accounts = await self.db.get_user_accounts(user_id)
        if not accounts:
            await update.message.reply_text("No accounts found")
            return
        message = "\n".join([
            f"📧 {a['email']} | {a['status']}" for a in accounts
        ])
        await update.message.reply_text(f"Your accounts:\n{message}")

    async def profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        accounts = await self.db.get_user_accounts(user_id)
        if not accounts:
            await update.message.reply_text("No accounts registered")
            return
        latest = accounts[0]
        await update.message.reply_text(
            f"Latest Account:\n"
            f"Email: {latest['email']}\n"
            f"Referral: {latest['referral_code']}\n"
            f"Proxy: {latest['proxy']}\n"
            f"Status: {latest['status']}"
        )

    async def delete_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        email = " ".join(context.args).strip()
        if not email:
            await update.message.reply_text("Please provide email to delete")
            return
        success = await self.db.delete_account(user_id, email)
        await update.message.reply_text(
            f"{'✅ Deleted' if success else '❌ Not found'}: {email}"
        )

    async def add_proxy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        proxy_file = await update.message.document.get_file()
        await proxy_file.download_to_drive("proxies.txt")
        self.proxy_manager.load_proxies_from_file("proxies.txt", user_id)
        await update.message.reply_text("Proxies added successfully!")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Error: {context.error}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ An error occurred: {str(context.error)[:200]}"
        )

    def run(self):
        self.telegram_app.add_error_handler(self.error_handler)
        asyncio.run(self.start())

if __name__ == "__main__":
    bot = GrassFarmBot()
    bot.run()
