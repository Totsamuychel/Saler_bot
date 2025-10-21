#!/usr/bin/env python3
"""
Скрипт для получения вашего Telegram ID
Запустите этот скрипт, затем напишите боту /start
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import config

# Отключаем лишние логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_user_id():
    """Получение ID пользователя"""
    
    if not config.BOT_TOKEN:
        print("❌ BOT_TOKEN не найден в .env файле!")
        return
    
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username or "нет"
        full_name = message.from_user.full_name or "нет"
        
        print(f"\n🎉 Получен ваш Telegram ID!")
        print(f"👤 ID: {user_id}")
        print(f"👤 Username: @{username}")
        print(f"👤 Имя: {full_name}")
        print(f"\n📝 Добавьте этот ID в .env файл:")
        print(f"ADMIN_IDS={user_id}")
        print(f"\n✅ Теперь вы можете остановить скрипт (Ctrl+C)")
        
        await message.answer(
            f"✅ Ваш Telegram ID: <code>{user_id}</code>\n\n"
            f"Добавьте этот ID в файл .env как ADMIN_IDS\n"
            f"Затем перезапустите бота.",
            parse_mode="HTML"
        )
    
    print("🤖 Бот запущен для получения вашего ID")
    print("📱 Напишите боту /start в Telegram")
    print("🛑 Нажмите Ctrl+C для остановки")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n👋 Скрипт остановлен")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(get_user_id())