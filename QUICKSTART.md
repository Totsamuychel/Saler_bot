# 🚀 Быстрый старт

## Минимальная установка (без конфликтов)

1. **Создайте виртуальное окружение:**
```bash
python -m venv bot_env
source bot_env/bin/activate  # Linux/Mac
# или
bot_env\Scripts\activate     # Windows
```

2. **Исправьте конфликты зависимостей:**
```bash
python fix_dependencies.py
```

3. **Настройте бота:**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

4. **Протестируйте:**
```bash
python test_bot.py
```

5. **Запустите:**
```bash
python main.py
```

## Минимальный .env файл

```env
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
ADMIN_IDS=123456789
OWNER_PHONE=+380123456789
OWNER_TELEGRAM=@owner
```

## Быстрая проверка

После установки выполните:
```bash
python -c "
import aiogram, aiosqlite, qrcode
from PIL import Image
print('✅ Все зависимости установлены')
"
```

## Если что-то не работает

1. **Конфликты пакетов:**
```bash
pip uninstall blendmodes chromadb fastapi langchain ollama -y
pip install -r requirements-minimal.txt
```

2. **Ошибки импорта:**
```bash
pip install --upgrade pip
pip install aiogram aiosqlite python-dotenv qrcode[pil] "pillow<10"
```

3. **Проблемы с базой:**
```bash
rm bot.db  # Удалить и пересоздать БД
```

## Автоматическое развертывание

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- Создаст виртуальное окружение
- Исправит конфликты зависимостей  
- Настроит конфигурацию
- Протестирует бота
- Подготовит к запуску