from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.admin_menu import get_admin_menu, get_broadcast_keyboard
from utils.translations import get_text
import config
import logging

logger = logging.getLogger(__name__)
router = Router()

class BroadcastStates(StatesGroup):
    waiting_message = State()

def is_admin(user_id: int) -> bool:
    """Checking administrator rights"""
    return user_id in config.ADMIN_IDS

@router.message(F.text.in_(["⚙️ Админ-панель", "⚙️ Адмін-панель"]))
async def admin_panel_handler(message: Message):
    """Login to the admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    admin_text = get_text("admin_panel", language)
    await message.answer(admin_text, reply_markup=get_admin_menu(language))

@router.message(F.text.in_(["📊 Статистика", "📊 Статистика"]))
async def stats_handler(message: Message):
    """Show statistics"""
    if not is_admin(message.from_user.id):
        return
    
    stats = await db.get_stats()
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    stats_text = get_text("statistics", language).format(
        total_users=stats.get("total_users", 0),
        active_talons=stats.get("active_talons", 0),
        total_revenue=stats.get("total_revenue", 0),
        today_sales=stats.get("today_sales", 0)
    )
    
    await message.answer(stats_text)

@router.message(F.text.in_(["👥 Пользователи", "👥 Користувачі"]))
async def users_handler(message: Message):
    """List of users"""
    if not is_admin(message.from_user.id):
        return
    
    users = await db.get_all_users()
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    if not users:
        await message.answer(get_text("no_users", language))
        return
    
    users_text = get_text("users_list", language) + "\n\n"
    
    for i, user_info in enumerate(users[:20], 1):  # Показываем первых 20
        username = user_info.get("username", "нет")
        full_name = user_info.get("full_name", "неизвестно")
        created_at = user_info.get("created_at", "")[:16]
        
        users_text += f"{i}. {full_name} (@{username})\n"
        users_text += f"   ID: {user_info['telegram_id']}\n"
        users_text += f"   Дата: {created_at}\n\n"
    
    if len(users) > 20:
        users_text += f"... и еще {len(users) - 20} пользователей"
    
    await message.answer(users_text)

@router.message(F.text.in_(["🧾 История платежей", "🧾 Історія платежів"]))
async def payments_history_handler(message: Message):
    """Payment history"""
    if not is_admin(message.from_user.id):
        return
    
    pending_payments = await db.get_pending_payments()
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    if not pending_payments:
        await message.answer(get_text("no_pending_payments", language))
        return
    
    payments_text = get_text("pending_payments", language) + "\n\n"
    
    for payment in pending_payments:
        username = payment.get("username", "нет")
        full_name = payment.get("full_name", "неизвестно")
        
        payments_text += f"💳 Платеж #{payment['id']}\n"
        payments_text += f"👤 {full_name} (@{username})\n"
        payments_text += f"⛽ {payment['liters']} л\n"
        payments_text += f"💰 {payment['amount']} грн\n"
        payments_text += f"📅 {payment['created_at'][:16]}\n\n"
    
    await message.answer(payments_text)

@router.message(F.text.in_(["📬 Рассылка", "📬 Розсилка"]))
async def broadcast_handler(message: Message, state: FSMContext):
    """Start of mailing"""
    if not is_admin(message.from_user.id):
        return
    
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    broadcast_text = get_text("broadcast_prompt", language)
    await message.answer(broadcast_text)
    await state.set_state(BroadcastStates.waiting_message)

@router.message(BroadcastStates.waiting_message)
async def broadcast_message_handler(message: Message, state: FSMContext):
    """Processing a message for distribution"""
    if not is_admin(message.from_user.id):
        return
    
    broadcast_message = message.text
    await state.update_data(broadcast_message=broadcast_message)
    
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    confirm_text = get_text("broadcast_confirm", language).format(
        message=broadcast_message
    )
    
    await message.answer(
        confirm_text,
        reply_markup=get_broadcast_keyboard(language)
    )

@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast_handler(callback: CallbackQuery, state: FSMContext):
    """Confirmation of mailing"""
    if not is_admin(callback.from_user.id):
        return
    
    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")
    
    if not broadcast_message:
        await callback.answer("Сообщение не найдено")
        return
    
    # We get all users
    users = await db.get_all_users()
    
    sent_count = 0
    failed_count = 0
    
    await callback.message.edit_text("📤 Начинаю рассылку...")
    
    for user_info in users:
        try:
            await callback.bot.send_message(
                user_info["telegram_id"],
                broadcast_message
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_info['telegram_id']}: {e}")
    
    result_text = (
        f"✅ Рассылка завершена!\n\n"
        f"📤 Отправлено: {sent_count}\n"
        f"❌ Не удалось: {failed_count}\n"
        f"👥 Всего пользователей: {len(users)}"
    )
    
    await callback.message.edit_text(result_text)
    await state.clear()

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast_handler(callback: CallbackQuery, state: FSMContext):
    """Cancel mailing list"""
    await callback.message.edit_text("❌ Рассылка отменена")
    await state.clear()

@router.message(F.text.in_(["➕ Управление талонами", "➕ Управління талонами"]))
async def manage_talons_handler(message: Message):
    """Coupon management"""
    if not is_admin(message.from_user.id):
        return
    
    user = await db.get_user(message.from_user.id)
    language = user.get("language", "ru") if user else "ru"
    
    manage_text = get_text("manage_talons", language)
    await message.answer(manage_text)
