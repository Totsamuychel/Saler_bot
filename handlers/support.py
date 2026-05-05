from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.translations import get_text
import config
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text.in_(["📞 Поддержка", "📞 Підтримка"]))
async def support_handler(message: Message):
    """Menu of support"""
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    support_text = get_text("support_menu", language)
    
    # Create a keyboard with contacts
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("call_owner", language),
                url=f"tel:{config.OWNER_PHONE}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("write_telegram", language),
                url=f"https://t.me/{config.OWNER_TELEGRAM.replace('@', '')}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("instagram", language),
                url=config.OWNER_INSTAGRAM
            )
        ]
    ])
    
    await message.answer(support_text, reply_markup=keyboard)
