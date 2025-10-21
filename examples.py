"""
Примеры использования функций бота
Для тестирования и демонстрации возможностей
"""

import asyncio
from database import db
from utils.price_calculator import calculate_price, get_price_per_liter, is_wholesale, calculate_savings
from utils.qr_generator import generate_qr_code
from utils.translations import get_text

async def example_database_operations():
    """Примеры работы с базой данных"""
    print("🗄️ Примеры работы с базой данных")
    print("=" * 40)
    
    # Инициализация БД
    await db.init_db()
    
    # Добавление пользователя
    user_id = 123456789
    await db.add_user(user_id, "testuser", "Test User", "ru")
    print(f"✅ Пользователь {user_id} добавлен")
    
    # Получение пользователя
    user = await db.get_user(user_id)
    print(f"👤 Пользователь: {user}")
    
    # Создание талона
    talon_id = await db.create_talon(user_id, 100, 5200)
    print(f"🎫 Талон создан с ID: {talon_id}")
    
    # Создание платежа
    payment_id = await db.create_payment(user_id, talon_id, 5200)
    print(f"💳 Платеж создан с ID: {payment_id}")
    
    # Получение талонов пользователя
    talons = await db.get_user_talons(user_id)
    print(f"🧾 Талоны пользователя: {len(talons)} шт.")
    
    # Статистика
    stats = await db.get_stats()
    print(f"📊 Статистика: {stats}")

def example_price_calculations():
    """Примеры расчета цен"""
    print("\n💰 Примеры расчета цен")
    print("=" * 40)
    
    test_quantities = [10, 50, 100, 200, 500]
    
    for qty in test_quantities:
        total = calculate_price(qty)
        per_liter = get_price_per_liter(qty)
        wholesale = is_wholesale(qty)
        savings = calculate_savings(qty)
        
        print(f"📊 {qty} л:")
        print(f"   💰 Общая стоимость: {total} грн")
        print(f"   💵 Цена за литр: {per_liter} грн")
        print(f"   🏪 Тип: {'Опт' if wholesale else 'Розница'}")
        if savings > 0:
            print(f"   💸 Экономия: {savings} грн")
        print()

async def example_qr_generation():
    """Примеры генерации QR-кодов"""
    print("📱 Примеры генерации QR-кодов")
    print("=" * 40)
    
    # Генерируем QR-коды для тестовых талонов
    test_talon_ids = [1, 2, 3]
    
    for talon_id in test_talon_ids:
        qr_path = await generate_qr_code(talon_id)
        if qr_path:
            print(f"✅ QR-код для талона {talon_id}: {qr_path}")
        else:
            print(f"❌ Ошибка создания QR-кода для талона {talon_id}")

def example_translations():
    """Примеры переводов"""
    print("\n🌐 Примеры переводов")
    print("=" * 40)
    
    test_keys = [
        "welcome",
        "price_list",
        "confirm_purchase",
        "payment_created"
    ]
    
    languages = ["ru", "uk"]
    
    for key in test_keys:
        print(f"🔑 Ключ: {key}")
        for lang in languages:
            text = get_text(key, lang)
            print(f"   {lang}: {text[:50]}...")
        print()

async def example_full_purchase_flow():
    """Пример полного процесса покупки"""
    print("🛒 Пример полного процесса покупки")
    print("=" * 40)
    
    # Инициализация
    await db.init_db()
    
    # Данные покупки
    user_id = 987654321
    username = "buyer"
    full_name = "Test Buyer"
    liters = 150
    language = "ru"
    
    print(f"👤 Покупатель: {full_name} (@{username})")
    print(f"⛽ Количество: {liters} л")
    
    # 1. Регистрация пользователя
    await db.add_user(user_id, username, full_name, language)
    print("✅ Пользователь зарегистрирован")
    
    # 2. Расчет цены
    total_price = calculate_price(liters)
    price_per_liter = get_price_per_liter(liters)
    is_wholesale_purchase = is_wholesale(liters)
    savings = calculate_savings(liters)
    
    print(f"💰 Цена за литр: {price_per_liter} грн")
    print(f"💵 Общая стоимость: {total_price} грн")
    print(f"🏪 Тип покупки: {'Опт' if is_wholesale_purchase else 'Розница'}")
    if savings > 0:
        print(f"💸 Экономия: {savings} грн")
    
    # 3. Создание талона
    talon_id = await db.create_talon(user_id, liters, total_price)
    print(f"🎫 Талон создан: #{talon_id}")
    
    # 4. Создание платежа
    payment_id = await db.create_payment(user_id, talon_id, total_price)
    print(f"💳 Платеж создан: #{payment_id}")
    
    # 5. Подтверждение платежа (админом)
    admin_id = 111111111
    success = await db.confirm_payment(payment_id, admin_id)
    if success:
        print("✅ Платеж подтвержден админом")
    
    # 6. Генерация QR-кода
    qr_path = await generate_qr_code(talon_id)
    if qr_path:
        print(f"📱 QR-код создан: {qr_path}")
    
    # 7. Проверка статуса
    talons = await db.get_user_talons(user_id)
    active_talons = [t for t in talons if t['status'] == 'active']
    print(f"🧾 Активных талонов: {len(active_talons)}")
    
    print("🎉 Покупка завершена успешно!")

async def main():
    """Запуск всех примеров"""
    print("🤖 Fuel Talon Bot - Примеры использования")
    print("=" * 50)
    
    try:
        # Примеры расчетов (не требуют БД)
        example_price_calculations()
        example_translations()
        
        # Примеры с БД
        await example_database_operations()
        await example_qr_generation()
        await example_full_purchase_flow()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n✅ Все примеры выполнены!")

if __name__ == "__main__":
    asyncio.run(main())