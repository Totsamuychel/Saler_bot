from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.translations import get_text
import config

def get_main_menu(language: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню для пользователей"""
    buttons = [
        [
            KeyboardButton(text=get_text("price_list_btn", language)),
            KeyboardButton(text=get_text("my_talons_btn", language))
        ],
        [
            KeyboardButton(text=get_text("how_it_works_btn", language)),
            KeyboardButton(text=get_text("support_btn", language))
        ],
        [
            KeyboardButton(text=get_text("language_btn", language)),
            KeyboardButton(text=get_text("referral_btn", language))
        ]
    ]
    
    # Добавляем кнопку админ-панели для администраторов
    # Эта кнопка будет видна всем, но работать только у админов
    buttons.append([
        KeyboardButton(text=get_text("admin_panel_btn", language))
    ])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )