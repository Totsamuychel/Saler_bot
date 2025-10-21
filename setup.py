#!/usr/bin/env python3
"""
Скрипт быстрой настройки проекта
Проверяет конфигурацию и помогает настроить бота
"""

import os
import sys
import asyncio
from pathlib import Path

def check_env_file():
    """Проверка .env файла"""
    print("📋 Проверка .env файла...")
    
    if not Path(".env").exists():
        print("❌ .env файл не найден!")
        if Path(".env.example").exists():
            print("📄 Копирую .env.example в .env")
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env файл создан. Отредактируйте его!")
            return False
        else:
            print("❌ .env.example тоже не найден!")
            return False
    
    # Читаем .env файл
    env_vars = {}
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value
    
    # Проверяем обязательные переменные
    required_vars = ["BOT_TOKEN", "ADMIN_IDS"]
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    # Проверяем BOT_TOKEN
    bot_token = env_vars.get("BOT_TOKEN", "")
    if not bot_token.count(":") == 1 or len(bot_token) < 40:
        print("❌ BOT_TOKEN выглядит некорректно")
        return False
    
    # Проверяем ADMIN_IDS
    admin_ids = env_vars.get("ADMIN_IDS", "")
    if admin_ids in ["123456789", "123456789,987654321"]:
        print("⚠️ ADMIN_IDS содержит тестовые значения!")
        print("🔧 Запустите 'python get_my_id.py' для получения вашего ID")
        return False
    
    print("✅ .env файл настроен корректно")
    return True

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    required_packages = [
        ("aiogram", "aiogram"),
        ("aiosqlite", "aiosqlite"), 
        ("qrcode", "qrcode"),
        ("PIL", "pillow"),
        ("dotenv", "python-dotenv")
    ]
    
    missing_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📥 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        print("или запустите: python fix_dependencies.py")
        return False
    
    return True

async def test_bot_connection():
    """Тест подключения к Telegram"""
    print("\n🤖 Тестирование подключения к Telegram...")
    
    try:
        import config
        from aiogram import Bot
        
        bot = Bot(token=config.BOT_TOKEN)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"📝 Имя бота: {bot_info.first_name}")
        print(f"🆔 ID бота: {bot_info.id}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

async def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    try:
        from database import db
        
        # Инициализация БД
        await db.init_db()
        print("✅ База данных инициализирована")
        
        # Тест операций
        test_user_id = 999999999
        await db.add_user(test_user_id, "test", "Test User")
        user = await db.get_user(test_user_id)
        
        if user:
            print("✅ Операции с БД работают")
            return True
        else:
            print("❌ Ошибка операций с БД")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        return False

def create_directories():
    """Создание необходимых директорий"""
    print("\n📁 Создание директорий...")
    
    directories = ["logs", "qr_codes"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")

async def main():
    """Основная функция настройки"""
    print("🚀 Настройка Fuel Talon Bot")
    print("=" * 50)
    
    # Проверки
    checks = [
        ("Конфигурация", check_env_file),
        ("Зависимости", check_dependencies),
        ("Подключение к Telegram", test_bot_connection),
        ("База данных", test_database)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            if not result:
                all_passed = False
                
        except Exception as e:
            print(f"❌ Ошибка в проверке '{name}': {e}")
            all_passed = False
    
    # Создаем директории
    create_directories()
    
    print(f"\n📊 Результат настройки:")
    if all_passed:
        print("🎉 Все проверки пройдены! Бот готов к запуску.")
        print("\n🚀 Команды для запуска:")
        print("  python main.py          # Обычный запуск")
        print("  python run.py           # Production запуск")
        print("  python test_bot.py      # Полное тестирование")
    else:
        print("⚠️ Некоторые проверки провалены.")
        print("\n🔧 Возможные решения:")
        print("  python fix_dependencies.py  # Исправить зависимости")
        print("  python get_my_id.py         # Получить ваш Telegram ID")
        print("  nano .env                   # Отредактировать конфигурацию")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Настройка прервана")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)