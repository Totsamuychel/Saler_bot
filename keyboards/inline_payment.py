from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.translations import get_text
import config

def get_fuel_selection(language: str = "ru") -> InlineKeyboardMarkup:
    """Выбор типа топлива"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("fuel_diesel", language),
                callback_data="fuel_diesel"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("fuel_gasoline", language),
                callback_data="fuel_gasoline"
            )
        ]
    ])

def get_quantity_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Выбор количества литров"""
    buttons = []
    
    # Быстрые варианты
    quick_options = [20, 50, 100, 200, 500]
    
    for i in range(0, len(quick_options), 2):
        row = []
        for j in range(2):
            if i + j < len(quick_options):
                qty = quick_options[i + j]
                row.append(InlineKeyboardButton(
                    text=f"{qty} л",
                    callback_data=f"qty_{qty}"
                ))
        buttons.append(row)
    
    # Кнопка для ввода своего количества
    buttons.append([
        InlineKeyboardButton(
            text=get_text("custom_quantity", language),
            callback_data="custom_qty"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения покупки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("confirm_payment_btn", language),
                callback_data="confirm_payment"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("cancel_payment_btn", language),
                callback_data="cancel_payment"
            )
        ]
    ])

def get_payment_confirmation_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для админа - подтверждение платежа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"confirm_admin_{payment_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"reject_admin_{payment_id}"
            )
        ]
    ])

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Выбор языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=config.LANGUAGES["ru"],
                callback_data="lang_ru"
            )
        ],
        [
            InlineKeyboardButton(
                text=config.LANGUAGES["uk"],
                callback_data="lang_uk"
            )
        ]
    ])