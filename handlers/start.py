from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database import db
from keyboards.main_menu import get_main_menu
from utils.translations import get_text
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Проверяем реферальный код
    referred_by = None
    if message.text and len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith("ref_"):
            try:
                referred_by = int(ref_code.replace("ref_", ""))
            except ValueError:
                pass
    
    # Добавляем пользователя в базу
    await db.add_user(user_id, username, full_name, referred_by=referred_by)
    
    # Получаем пользователя для определения языка
    user = await db.get_user(user_id)
    language = user.get("language", "ru") if user else "ru"
    
    # Приветственное сообщение
    welcome_text = get_text("welcome", language)
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(language)
    )
    
    logger.info(f"New user started bot: {user_id} (@{username})")

@router.message(F.text == "🏠 Главное меню")
@router.message(F.text == "🏠 Головне меню")
async def main_menu_handler(message: Message):
    """Возврат в главное меню"""
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    menu_text = get_text("main_menu", language)
    
    await message.answer(
        menu_text,
        reply_markup=get_main_menu(language)
    )