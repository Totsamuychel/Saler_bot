#!/usr/bin/env python3
"""
Простой тест для проверки работоспособности бота
Проверяет импорты, конфигурацию и базовые функции
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Тест импортов"""
    print("📦 Тестирование импортов...")
    
    try:
        import aiogram
        print(f"✅ aiogram {aiogram.__version__}")
    except ImportError as e:
        print(f"❌ aiogram: {e}")
        return False
    
    try:
        import aiosqlite
        print("✅ aiosqlite")
    except ImportError as e:
        print(f"❌ aiosqlite: {e}")
        return False
    
    try:
        import qrcode
        print("✅ qrcode")
    except ImportError as e:
        print(f"❌ qrcode: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL)")
    except ImportError as e:
        print(f"❌ Pillow: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
        return False
    
    return True

def test_config():
    """Тест конфигурации"""
    print("\n⚙️ Тестирование конфигурации...")
    
    try:
        import config
        
        # Проверяем основные настройки
        if hasattr(config, 'BOT_TOKEN'):
            if config.BOT_TOKEN:
                print("✅ BOT_TOKEN установлен")
            else:
                print("⚠️ BOT_TOKEN пустой")
        else:
            print("❌ BOT_TOKEN не найден")
            return False
        
        if hasattr(config, 'ADMIN_IDS'):
            if config.ADMIN_IDS:
                print(f"✅ ADMIN_IDS: {len(config.ADMIN_IDS)} админов")
            else:
                print("⚠️ ADMIN_IDS пустой")
        else:
            print("❌ ADMIN_IDS не найден")
        
        # Проверяем цены
        if hasattr(config, 'RETAIL_PRICE') and config.RETAIL_PRICE > 0:
            print(f"✅ RETAIL_PRICE: {config.RETAIL_PRICE}")
        else:
            print("❌ RETAIL_PRICE некорректная")
            return False
        
        if hasattr(config, 'WHOLESALE_PRICE') and config.WHOLESALE_PRICE > 0:
            print(f"✅ WHOLESALE_PRICE: {config.WHOLESALE_PRICE}")
        else:
            print("❌ WHOLESALE_PRICE некорректная")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта config: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

async def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    try:
        from database import db
        
        # Инициализация БД
        await db.init_db()
        print("✅ База данных инициализирована")
        
        # Тест добавления пользователя
        test_user_id = 999999999
        success = await db.add_user(test_user_id, "testuser", "Test User", "ru")
        if success:
            print("✅ Добавление пользователя работает")
        else:
            print("⚠️ Пользователь уже существует или ошибка")
        
        # Тест получения пользователя
        user = await db.get_user(test_user_id)
        if user:
            print("✅ Получение пользователя работает")
        else:
            print("❌ Ошибка получения пользователя")
            return False
        
        # Тест статистики
        stats = await db.get_stats()
        if isinstance(stats, dict):
            print(f"✅ Статистика: {stats.get('total_users', 0)} пользователей")
        else:
            print("❌ Ошибка получения статистики")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_utils():
    """Тест утилит"""
    print("\n🛠️ Тестирование утилит...")
    
    try:
        from utils.price_calculator import calculate_price, get_price_per_liter
        from utils.translations import get_text
        
        # Тест калькулятора цен
        price = calculate_price(100)
        if price > 0:
            print(f"✅ Калькулятор цен: 100л = {price} грн")
        else:
            print("❌ Ошибка калькулятора цен")
            return False
        
        # Тест переводов
        text_ru = get_text("welcome", "ru")
        text_uk = get_text("welcome", "uk")
        if text_ru and text_uk and text_ru != text_uk:
            print("✅ Переводы работают")
        else:
            print("❌ Ошибка переводов")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка утилит: {e}")
        return False

async def test_qr_generation():
    """Тест генерации QR-кодов"""
    print("\n📱 Тестирование QR-кодов...")
    
    try:
        from utils.qr_generator import generate_qr_code
        
        # Создаем тестовый QR-код
        qr_path = await generate_qr_code(999)
        if qr_path and Path(qr_path).exists():
            print(f"✅ QR-код создан: {qr_path}")
            # Удаляем тестовый файл
            Path(qr_path).unlink()
            return True
        else:
            print("❌ Ошибка создания QR-кода")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка QR-генератора: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование Fuel Talon Bot")
    print("=" * 50)
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_config),
        ("База данных", test_database),
        ("Утилиты", test_utils),
        ("QR-коды", test_qr_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{name}': {e}")
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Провалено: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Все тесты пройдены! Бот готов к запуску.")
        return 0
    else:
        print(f"\n⚠️ Некоторые тесты провалены. Проверьте конфигурацию.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)