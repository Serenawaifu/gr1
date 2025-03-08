import aiosqlite
from loguru import logger

class Database:
    async def initialize(self):
        self.conn = await aiosqlite.connect("grass.db")
        await self.create_tables()

    async def create_tables(self):
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER NOT NULL,
                email TEXT UNIQUE,
                password TEXT,
                referral_code TEXT,
                proxy TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER NOT NULL,
                protocol TEXT,
                user TEXT,
                password TEXT,
                ip TEXT,
                port INTEGER,
                FOREIGN KEY(telegram_id) REFERENCES accounts(telegram_id)
            )
        """)
        await self.conn.commit()

    async def add_account(self, user_id, email, password, referral, proxy):
        try:
            await self.conn.execute("""
                INSERT INTO accounts (
                    telegram_id, email, password, referral_code, proxy
                ) VALUES (?, ?, ?, ?, ?)
            """, (user_id, email, password, referral, proxy))
            await self.conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def get_user_accounts(self, user_id):
        cursor = await self.conn.execute(
            "SELECT * FROM accounts WHERE telegram_id = ?",
            (user_id,)
        )
        return await cursor.fetchall()

    async def delete_account(self, user_id, email):
        cursor = await self.conn.execute(
            "DELETE FROM accounts WHERE telegram_id = ? AND email = ?",
            (user_id, email)
        )
        await self.conn.commit()
        return cursor.rowcount > 0

    async def close(self):
        await self.conn.close()
