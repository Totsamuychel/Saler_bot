from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.translations import get_text

def get_admin_menu(language: str = "ru") -> ReplyKeyboardMarkup:
    """Admin-panel"""
    buttons = [
        [
            KeyboardButton(text=get_text("statistics_btn", language)),
            KeyboardButton(text=get_text("users_btn", language))
        ],
        [
            KeyboardButton(text=get_text("payments_history_btn", language)),
            KeyboardButton(text=get_text("manage_talons_btn", language))
        ],
        [
            KeyboardButton(text=get_text("broadcast_btn", language))
        ],
        [
            KeyboardButton(text=get_text("main_menu_btn", language))
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_broadcast_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Mailing confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("confirm_btn", language),
                callback_data="confirm_broadcast"
            ),
            InlineKeyboardButton(
                text=get_text("cancel_btn", language),
                callback_data="cancel_broadcast"
            )
        ]
    ])
