from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.translations import get_text
import config

def get_main_menu(language: str = "ru") -> ReplyKeyboardMarkup:
    """Main menu for users"""
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
    
    # Adding an admin panel button for administrators
    # This button will be visible to everyone, but will only work for admins.
    buttons.append([
        KeyboardButton(text=get_text("admin_panel_btn", language))
    ])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )
