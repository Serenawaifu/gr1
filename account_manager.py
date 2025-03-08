import aiohttp
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from loguru import logger
from captchatools import CaptchaSolver as CaptchaAPI  # <button class="citation-flag" data-index="6">

class AccountManager:
    def __init__(self, db, proxy_manager, captcha_solver):
        self.db = db
        self.proxy_manager = proxy_manager
        self.captcha_solver = captcha_solver

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True
    )
    async def add_account_from_input(
        self, user_id, input_str, telegram_update
    ):
        parts = input_str.split(":")
        if len(parts) == 2:
            email, password = parts
            referral = None
        elif len(parts) == 3:
            email, referral, password = parts
        else:
            await telegram_update.message.reply_text("Invalid format")
            return

        proxy = await self.proxy_manager.get_random_proxy(user_id)
        try:
            await self.register_account(
                email, password, referral, proxy
            )
            await self.db.add_account(
                user_id, email, password, referral, proxy
            )
            await telegram_update.message.reply_text(
                f"✅ Added {email} with proxy {proxy}"
            )
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            await telegram_update.message.reply_text(
                f"❌ Failed: {str(e)[:100]}"
            )

    async def register_account(
        self, email, password, referral, proxy
    ):
        async with aiohttp.ClientSession() as session:
            # Get CAPTCHA image
            async with session.get(
                "https://app.getgrass.io/captcha",
                proxy=proxy
            ) as resp:
                captcha_image = await resp.read()

            # Solve CAPTCHA
            solution = self.captcha_solver.solve(captcha_image)

            # Submit registration
            await session.post(
                "https://app.getgrass.io/register",
                data={
                    "email": email,
                    "password": password,
                    "referral_code": referral or "",
                    "captcha": solution
                },
                proxy=proxy
            )
