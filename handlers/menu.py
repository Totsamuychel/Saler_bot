from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.main_menu import get_main_menu
from keyboards.inline_payment import get_fuel_selection, get_quantity_keyboard, get_payment_keyboard
from utils.translations import get_text
from utils.price_calculator import calculate_price
import config
import logging

logger = logging.getLogger(__name__)
router = Router()

class PurchaseStates(StatesGroup):
    selecting_fuel = State()
    entering_quantity = State()
    confirming_purchase = State()

@router.message(F.text.in_(["💰 Прайс-лист", "💰 Прайс-лист"]))
async def price_list_handler(message: Message, state: FSMContext):
    """Show the price list and start shopping"""
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    price_text = get_text("price_list", language).format(
        retail_price=config.RETAIL_PRICE,
        wholesale_price=config.WHOLESALE_PRICE,
        threshold=config.WHOLESALE_THRESHOLD
    )
    
    await message.answer(
        price_text,
        reply_markup=get_fuel_selection(language)
    )
    await state.set_state(PurchaseStates.selecting_fuel)

@router.callback_query(F.data.startswith("fuel_"))
async def fuel_selected(callback: CallbackQuery, state: FSMContext):
    """Selecting a fuel type"""
    fuel_type = callback.data.split("_")[1]
    await state.update_data(fuel_type=fuel_type)
    
    user = await db.get_user(callback.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    quantity_text = get_text("enter_quantity", language)
    
    await callback.message.edit_text(
        quantity_text,
        reply_markup=get_quantity_keyboard(language)
    )
    await state.set_state(PurchaseStates.entering_quantity)

@router.callback_query(F.data.startswith("qty_"))
async def quantity_selected(callback: CallbackQuery, state: FSMContext):
    """Select the number of liters"""
    quantity = int(callback.data.split("_")[1])
    data = await state.get_data()
    fuel_type = data.get("fuel_type")
    
    # We calculate the price
    total_price = calculate_price(quantity)
    
    await state.update_data(quantity=quantity, total_price=total_price)
    
    user = await db.get_user(callback.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    # Determine the price type
    price_type = "wholesale" if quantity >= config.WHOLESALE_THRESHOLD else "retail"
    price_per_liter = config.WHOLESALE_PRICE if quantity >= config.WHOLESALE_THRESHOLD else config.RETAIL_PRICE
    
    confirm_text = get_text("confirm_purchase", language).format(
        fuel_type=get_text(f"fuel_{fuel_type}", language),
        quantity=quantity,
        price_per_liter=price_per_liter,
        price_type=get_text(price_type, language),
        total_price=total_price
    )
    
    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_payment_keyboard(language)
    )
    await state.set_state(PurchaseStates.confirming_purchase)

@router.message(F.text.regexp(r'^\d+$'))
async def custom_quantity_handler(message: Message, state: FSMContext):
    """Processing a custom amount of liters"""
    current_state = await state.get_state()
    if current_state != PurchaseStates.entering_quantity:
        return
    
    try:
        quantity = int(message.text)
        if quantity <= 0 or quantity > 1000:
            user = await db.get_user(message.from_user.id)
            language = user.get("language", "ru") if user else "ru"
            error_text = get_text("invalid_quantity", language)
            await message.answer(error_text)
            return
        
        data = await state.get_data()
        fuel_type = data.get("fuel_type")
        
        # We calculate the price
        total_price = calculate_price(quantity)
        
        await state.update_data(quantity=quantity, total_price=total_price)
        
        user = await db.get_user(message.from_user.id)
        language = user.get("language", "ru") if user else "ru"
        
        # Determine the price type
        price_type = "wholesale" if quantity >= config.WHOLESALE_THRESHOLD else "retail"
        price_per_liter = config.WHOLESALE_PRICE if quantity >= config.WHOLESALE_THRESHOLD else config.RETAIL_PRICE
        
        confirm_text = get_text("confirm_purchase", language).format(
            fuel_type=get_text(f"fuel_{fuel_type}", language),
            quantity=quantity,
            price_per_liter=price_per_liter,
            price_type=get_text(price_type, language),
            total_price=total_price
        )
        
        await message.answer(
            confirm_text,
            reply_markup=get_payment_keyboard(language)
        )
        await state.set_state(PurchaseStates.confirming_purchase)
        
    except ValueError:
        user = await db.get_user(message.from_user.id)
        language = user.get("language", "ru") if user else "ru"
        error_text = get_text("invalid_quantity", language)
        await message.answer(error_text)

@router.message(F.text.in_(["🧾 Мои талоны", "🧾 Мої талони"]))
async def my_talons_handler(message: Message):
    """Show user tickets"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user.get("language", "ru") if user else "ru"
    
    talons = await db.get_user_talons(user_id)
    
    if not talons:
        no_talons_text = get_text("no_talons", language)
        await message.answer(no_talons_text)
        return
    
    talons_text = get_text("your_talons", language) + "\n\n"
    
    for talon in talons:
        status_emoji = "✅" if talon["status"] == "active" else "❌"
        status_text = get_text(f"status_{talon['status']}", language)
        
        talons_text += f"🎫 Талон #{talon['id']}\n"
        talons_text += f"⛽ {talon['liters']} л\n"
        talons_text += f"💰 {talon['price']} грн\n"
        talons_text += f"{status_emoji} {status_text}\n"
        talons_text += f"📅 {talon['created_at'][:16]}\n\n"
    
    await message.answer(talons_text)

@router.message(F.text.in_(["💡 Как работает бот", "💡 Як працює бот"]))
async def how_it_works_handler(message: Message):
    """Instructions for using the bot"""
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    instruction_text = get_text("how_it_works", language)
    await message.answer(instruction_text)

@router.message(F.text.in_(["🌐 Язык", "🌐 Мова"]))
async def language_handler(message: Message):
    """Language selection"""
    from keyboards.inline_payment import get_language_keyboard
    
    await message.answer(
        "🌐 Выберите язык / Оберіть мову:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    """Change language"""
    language = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    await db.update_user_language(user_id, language)
    
    success_text = get_text("language_changed", language)
    await callback.message.edit_text(success_text)
    
    # We present the updated main menu
    await callback.message.answer(
        get_text("main_menu", language),
        reply_markup=get_main_menu(language)
    )

@router.message(F.text.in_(["🎁 Пригласи друга", "🎁 Запроси друга"]))
async def referral_handler(message: Message):
    """Referral system"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user.get("language", "ru") if user else "ru"
    
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    referral_text = get_text("referral_info", language).format(
        ref_link=ref_link,
        bonus=config.REFERRAL_BONUS
    )
    
    await message.answer(referral_text)
