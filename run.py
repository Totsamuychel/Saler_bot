#!/usr/bin/env python3
"""
Production runner для Telegram-бота
Включает дополнительные проверки и обработку ошибок
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from main import main
import config

def setup_logging():
    """Настройка продакшн логирования"""
    
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Файловый хендлер
    file_handler = logging.FileHandler(log_dir / "bot.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Хендлер для ошибок
    error_handler = logging.FileHandler(log_dir / "errors.log", encoding='utf-8')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Отключаем лишние логи от библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

def check_config():
    """Проверка конфигурации перед запуском"""
    errors = []
    
    if not config.BOT_TOKEN:
        errors.append("BOT_TOKEN не установлен")
    
    if not config.ADMIN_IDS:
        errors.append("ADMIN_IDS не установлены")
    
    if config.RETAIL_PRICE <= 0:
        errors.append("RETAIL_PRICE должна быть больше 0")
    
    if config.WHOLESALE_PRICE <= 0:
        errors.append("WHOLESALE_PRICE должна быть больше 0")
    
    if config.WHOLESALE_THRESHOLD <= 0:
        errors.append("WHOLESALE_THRESHOLD должен быть больше 0")
    
    if errors:
        print("❌ Ошибки конфигурации:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ Конфигурация проверена")

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    print(f"\n🛑 Получен сигнал {signum}. Завершение работы...")
    sys.exit(0)

async def run_with_restart():
    """Запуск с автоматическим перезапуском при ошибках"""
    restart_count = 0
    max_restarts = 5
    
    while restart_count < max_restarts:
        try:
            print(f"🚀 Запуск бота (попытка {restart_count + 1})")
            await main()
            break
            
        except KeyboardInterrupt:
            print("👋 Бот остановлен пользователем")
            break
            
        except Exception as e:
            restart_count += 1
            print(f"❌ Ошибка: {e}")
            
            if restart_count < max_restarts:
                wait_time = min(restart_count * 10, 60)  # Экспоненциальная задержка
                print(f"⏳ Перезапуск через {wait_time} секунд...")
                await asyncio.sleep(wait_time)
            else:
                print(f"💥 Превышено максимальное количество перезапусков ({max_restarts})")
                break

if __name__ == "__main__":
    print("🤖 Fuel Talon Bot - Production Runner")
    print("=" * 50)
    
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Настраиваем логирование
    setup_logging()
    
    # Проверяем конфигурацию
    check_config()
    
    # Запускаем бота
    try:
        asyncio.run(run_with_restart())
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)