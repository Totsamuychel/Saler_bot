#!/bin/bash

# Скрипт развертывания Fuel Talon Bot
# Использование: ./deploy.sh

set -e

echo "🚀 Развертывание Fuel Talon Bot"
echo "================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
if [[ $EUID -eq 0 ]]; then
   log_error "Не запускайте этот скрипт от root!"
   exit 1
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 не найден. Установите Python 3.10+"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    log_error "Требуется Python $REQUIRED_VERSION+, найден $PYTHON_VERSION"
    exit 1
fi

log_info "Python версия: $PYTHON_VERSION ✓"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    log_info "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
log_info "Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
log_info "Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
log_info "Установка зависимостей..."

# Проверяем наличие скрипта исправления конфликтов
if [ -f "fix_dependencies.py" ]; then
    log_info "Исправление возможных конфликтов зависимостей..."
    python3 fix_dependencies.py
else
    # Обычная установка
    if [ -f "requirements-minimal.txt" ]; then
        log_info "Установка минимальных зависимостей..."
        pip install -r requirements-minimal.txt
    else
        pip install -r requirements.txt
    fi
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    log_warn ".env файл не найден"
    if [ -f ".env.example" ]; then
        log_info "Копирование .env.example в .env"
        cp .env.example .env
        log_warn "Отредактируйте .env файл перед запуском бота!"
    else
        log_error ".env.example не найден"
        exit 1
    fi
else
    log_info ".env файл найден ✓"
fi

# Создание директорий
log_info "Создание необходимых директорий..."
mkdir -p logs
mkdir -p qr_codes

# Проверка конфигурации
log_info "Проверка конфигурации..."
python3 -c "
import config
import sys

errors = []
if not config.BOT_TOKEN:
    errors.append('BOT_TOKEN не установлен')
if not config.ADMIN_IDS:
    errors.append('ADMIN_IDS не установлены')

if errors:
    print('❌ Ошибки конфигурации:')
    for error in errors:
        print(f'  - {error}')
    sys.exit(1)
else:
    print('✅ Конфигурация корректна')
"

if [ $? -ne 0 ]; then
    log_error "Исправьте ошибки конфигурации в .env файле"
    exit 1
fi

# Запуск тестов
if [ -f "test_bot.py" ]; then
    log_info "Запуск тестов..."
    python3 test_bot.py
    if [ $? -ne 0 ]; then
        log_error "Тесты провалены. Проверьте конфигурацию."
        exit 1
    fi
else
    # Тестовый запуск (старый метод)
    log_info "Тестовый запуск бота..."
    timeout 10s python3 main.py || {
        if [ $? -eq 124 ]; then
            log_info "Тестовый запуск успешен (таймаут 10с) ✓"
        else
            log_error "Ошибка при тестовом запуске"
            exit 1
        fi
    }
fi

# Предложение установки systemd service
echo ""
log_info "Развертывание завершено успешно! 🎉"
echo ""
echo "Для запуска бота:"
echo "  python3 main.py          # Обычный запуск"
echo "  python3 run.py           # Production запуск"
echo ""
echo "Для установки как systemd service:"
echo "  sudo cp fuel-bot.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable fuel-bot"
echo "  sudo systemctl start fuel-bot"
echo ""
log_warn "Не забудьте настроить .env файл с вашими данными!"