# -*- coding: utf-8 -*-
import aiosqlite
import logging

log = logging.getLogger(__name__)
DB_FILE = "hsr_bot.db"

async def init_db():
    """Инициализация базы данных."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                notifications INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                character_name TEXT,
                UNIQUE(user_id, character_name)
            )
        """)
        await db.commit()
        log.info("База данных инициализирована")

async def add_user(user_id: int):
    """Добавить пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()

async def get_all_users() -> list:
    """Получить всех пользователей с включенными уведомлениями."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE notifications = 1"
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def toggle_notifications(user_id: int) -> bool:
    """Переключить уведомления. Возвращает новое состояние."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT notifications FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            new_state = 0 if row[0] == 1 else 1
        await db.execute(
            "UPDATE users SET notifications = ? WHERE user_id = ?",
            (new_state, user_id)
        )
        await db.commit()
        return bool(new_state)

async def subscribe_character(user_id: int, character: str):
    """Подписаться на уведомление о персонаже."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO subscriptions (user_id, character_name) VALUES (?, ?)",
            (user_id, character.lower())
        )
        await db.commit()

async def unsubscribe_character(user_id: int, character: str):
    """Отписаться от уведомления о персонаже."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "DELETE FROM subscriptions WHERE user_id = ? AND character_name = ?",
            (user_id, character.lower())
        )
        await db.commit()

async def get_subscriptions(user_id: int) -> list:
    """Получить подписки пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT character_name FROM subscriptions WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
