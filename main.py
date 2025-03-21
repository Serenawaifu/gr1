import asyncio
import signal
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
        self.captcha_solver = CaptchaSolver("YOUR_2CAPTCHA_API_KEY")  # Captcha Solver API Key
        self.account_manager = AccountManager(
            self.db, 
            self.proxy_manager, 
            self.captcha_solver
        )
        self.telegram_app = ApplicationBuilder().token("YOUR_TELEGRAM_TOKEN").build()  # Telegram Bot Token

    async def start(self):
        await self.db.initialize()
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
        try:
            raise context.error
        except asyncio.CancelledError:
            logger.warning("Asyncio task was cancelled.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            if update and hasattr(update, 'effective_chat') and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⚠️ An error occurred: {str(e)}"
                )

    async def shutdown(self, sig):
        """Cleanup tasks tied to the service's shutdown."""
        logger.info(f"Received exit signal {sig.name}...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        
        # Stop the updater first
        logger.info("Stopping updater...")
        if hasattr(self.telegram_app, 'updater') and self.telegram_app.updater:
            await self.telegram_app.updater.stop()
        
        # Stop the application
        logger.info("Stopping application...")
        await self.telegram_app.stop()
        
        # Cancel any remaining tasks
        if tasks:
            logger.info(f"Cancelling {len(tasks)} outstanding tasks...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Shutdown complete.")

    def run(self):
        # Set up error handler
        self.telegram_app.add_error_handler(self.error_handler)
        
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Set up proper signal handling for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(self.shutdown(s))
            )
        
        try:
            # Run the bot with the new event loop
            loop.run_until_complete(self.start())
            loop.run_forever()
        finally:
            # Clean up
            loop.close()
            logger.info("Successfully shut down the bot")

if __name__ == "__main__":
    bot = GrassFarmBot()
    bot.run()
