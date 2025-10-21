#!/usr/bin/env python3
"""
Скрипт для исправления конфликтов зависимостей
Удаляет конфликтующие пакеты и устанавливает только необходимые
"""

import subprocess
import sys
import os

def run_command(command):
    """Выполнение команды с выводом результата"""
    print(f"🔧 Выполняю: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Ошибка: {result.stderr}")
        return False
    else:
        print(f"✅ Успешно")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True

def main():
    print("🔧 Исправление конфликтов зависимостей")
    print("=" * 50)
    
    # Список конфликтующих пакетов для удаления
    conflicting_packages = [
        "blendmodes",
        "chromadb", 
        "fastapi",
        "langchain",
        "langchain-core",
        "ollama",
        "asyncio-mqtt",
        "sqlalchemy"
    ]
    
    # Удаляем конфликтующие пакеты
    print("🗑️ Удаление конфликтующих пакетов...")
    for package in conflicting_packages:
        run_command(f"pip uninstall -y {package}")
    
    # Обновляем pip
    print("\n📦 Обновление pip...")
    run_command("pip install --upgrade pip")
    
    # Устанавливаем только необходимые зависимости
    print("\n📥 Установка необходимых зависимостей...")
    
    if os.path.exists("requirements-minimal.txt"):
        success = run_command("pip install -r requirements-minimal.txt")
    else:
        # Устанавливаем вручную
        packages = [
            "aiogram==3.4.1",
            "aiosqlite==0.19.0", 
            "python-dotenv==1.0.0",
            "qrcode[pil]==7.4.2",
            "pillow>=9.0.0,<10.0.0"
        ]
        
        success = True
        for package in packages:
            if not run_command(f"pip install {package}"):
                success = False
                break
    
    if success:
        print("\n✅ Зависимости успешно исправлены!")
        print("\nТеперь можно запускать бота:")
        print("  python main.py")
    else:
        print("\n❌ Произошли ошибки при установке")
        return 1
    
    # Проверяем установленные пакеты
    print("\n📋 Проверка установленных пакетов...")
    run_command("pip list | grep -E '(aiogram|aiosqlite|dotenv|qrcode|pillow)'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())