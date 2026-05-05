from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline_payment import get_payment_confirmation_keyboard
from utils.translations import get_text
from utils.qr_generator import generate_qr_code
import config
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "confirm_payment")
async def confirm_payment_handler(callback: CallbackQuery, state: FSMContext):
    """Confirmation of payment by the user"""
    data = await state.get_data()
    user_id = callback.from_user.id
    
    quantity = data.get("quantity")
    total_price = data.get("total_price")
    fuel_type = data.get("fuel_type", "diesel")
    
    if not quantity or not total_price:
        await callback.answer("Ошибка: данные о покупке не найдены")
        return
    
    # Create a coupon
    talon_id = await db.create_talon(user_id, quantity, total_price)
    if not talon_id:
        await callback.answer("Ошибка создания талона")
        return
    
    # Create a payment record
    payment_id = await db.create_payment(user_id, talon_id, total_price)
    if not payment_id:
        await callback.answer("Ошибка создания платежа")
        return
    
    user = await db.get_user(user_id)
    language = user.get("language", "ru") if user else "ru"
    
    # Notifying the user
    payment_text = get_text("payment_created", language).format(
        talon_id=talon_id,
        quantity=quantity,
        total_price=total_price
    )
    
    await callback.message.edit_text(payment_text)
    
    # We notify admins about a new payment
    await notify_admins_about_payment(callback.bot, user_id, payment_id, total_price, quantity)
    
    await state.clear()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment_handler(callback: CallbackQuery, state: FSMContext):
    """Payment cancellation"""
    user = await db.get_user(callback.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    cancel_text = get_text("payment_cancelled", language)
    await callback.message.edit_text(cancel_text)
    await state.clear()

@router.callback_query(F.data.startswith("confirm_admin_"))
async def admin_confirm_payment(callback: CallbackQuery):
    """Payment confirmation by the administrator"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет прав для этого действия")
        return
    
    payment_id = int(callback.data.split("_")[2])
    admin_id = callback.from_user.id
    
    # Confirming the payment
    success = await db.confirm_payment(payment_id, admin_id)
    
    if success:
        # Receiving payment information
        payments = await db.get_pending_payments()
        payment_info = None
        
        for payment in payments:
            if payment["id"] == payment_id:
                payment_info = payment
                break
        
        if payment_info:
            # Generate a QR code for the coupon
            qr_path = await generate_qr_code(payment_info["talon_id"])
            
            # We notify the user about the activation of the coupon
            await notify_user_about_activation(
                callback.bot, 
                payment_info["user_id"], 
                payment_info["talon_id"],
                payment_info["liters"],
                qr_path
            )
        
        await callback.message.edit_text(
            f"✅ Платеж #{payment_id} подтвержден!\n"
            f"Талон активирован и отправлен пользователю."
        )
    else:
        await callback.answer("Ошибка подтверждения платежа")

@router.callback_query(F.data.startswith("reject_admin_"))
async def admin_reject_payment(callback: CallbackQuery):
    """Payment declined by admin"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет прав для этого действия")
        return
    
    payment_id = int(callback.data.split("_")[2])
    
    
    await callback.message.edit_text(
        f"❌ Платеж #{payment_id} отклонен."
    )

async def notify_admins_about_payment(bot, user_id: int, payment_id: int, amount: int, liters: int):
    """Notifying admins about a new payment"""
    user = await db.get_user(user_id)
    username = user.get("username", "неизвестно") if user else "неизвестно"
    full_name = user.get("full_name", "неизвестно") if user else "неизвестно"
    
    admin_text = (
        f"💰 Новый платеж!\n\n"
        f"👤 Пользователь: {full_name} (@{username})\n"
        f"🆔 ID: {user_id}\n"
        f"⛽ Количество: {liters} л\n"
        f"💵 Сумма: {amount} грн\n"
        f"🔢 Платеж ID: {payment_id}\n\n"
        f"Подтвердить оплату?"
    )
    
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=get_payment_confirmation_keyboard(payment_id)
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def notify_user_about_activation(bot, user_id: int, talon_id: int, liters: int, qr_path: str):
    """Notifying the user about the activation of the coupon"""
    user = await db.get_user(user_id)
    language = user.get("language", "ru") if user else "ru"
    
    activation_text = get_text("talon_activated", language).format(
        talon_id=talon_id,
        liters=liters
    )
    
    try:
        # Sending a QR code
        if qr_path:
            with open(qr_path, 'rb') as qr_file:
                await bot.send_photo(
                    user_id,
                    qr_file,
                    caption=activation_text
                )
        else:
            await bot.send_message(user_id, activation_text)
            
    except Exception as e:
        logger.error(f"Failed to notify user {user_id} about activation: {e}")
