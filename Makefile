# Makefile для удобного управления ботом

.PHONY: help install setup test run clean

help:  ## Показать справку
	@echo "🤖 Fuel Talon Bot - Команды управления"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	python fix_dependencies.py

setup:  ## Настроить проект
	@echo "⚙️ Настройка проекта..."
	python setup.py

test:  ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	python test_bot.py

run:  ## Запустить бота (обычный режим)
	@echo "🚀 Запуск бота..."
	python main.py

run-prod:  ## Запустить бота (production режим)
	@echo "🚀 Запуск бота (production)..."
	python run.py

get-id:  ## Получить ваш Telegram ID
	@echo "🆔 Получение Telegram ID..."
	python get_my_id.py

clean:  ## Очистить временные файлы
	@echo "🧹 Очистка..."
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf logs/*.log
	rm -rf qr_codes/*.png

clean-db:  ## Очистить базу данных
	@echo "🗄️ Очистка базы данных..."
	rm -f bot.db

restart: clean-db run  ## Перезапуск с чистой БД

deploy:  ## Развернуть проект
	@echo "🚀 Развертывание..."
	chmod +x deploy.sh
	./deploy.sh

status:  ## Показать статус systemd service
	systemctl status fuel-bot

logs:  ## Показать логи
	@echo "📋 Последние логи:"
	@if [ -f "logs/bot.log" ]; then tail -n 50 logs/bot.log; else echo "Логи не найдены"; fi

install-service:  ## Установить systemd service
	@echo "⚙️ Установка systemd service..."
	sudo cp fuel-bot.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable fuel-bot
	@echo "✅ Service установлен. Запуск: sudo systemctl start fuel-bot"

# Алиасы для Windows (если make недоступен)
win-install:  ## Windows: установить зависимости
	python fix_dependencies.py

win-setup:  ## Windows: настроить проект
	python setup.py

win-test:  ## Windows: запустить тесты
	python test_bot.py

win-run:  ## Windows: запустить бота
	python main.py