# Makefile for easy bot management

.PHONY: help install setup test run clean

help:  ## Показать справку
	@echo "🤖 Fuel Talon Bot - Команды управления"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## set dependencies
	@echo "📦 Установка зависимостей..."
	python fix_dependencies.py

setup:  ## set project
	@echo "⚙️ Настройка проекта..."
	python setup.py

test:  ## launch tests
	@echo "🧪 Запуск тестов..."
	python test_bot.py

run:  ## Launch a bot (default mode)
	@echo "🚀 Запуск бота..."
	python main.py

run-prod:  ## Launch a bot (production mode)
	@echo "🚀 Запуск бота (production)..."
	python run.py

get-id:  ## Get your Telegram ID
	@echo "🆔 Получение Telegram ID..."
	python get_my_id.py

clean:  ## Delete temporary files
	@echo "🧹 Очистка..."
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf logs/*.log
	rm -rf qr_codes/*.png

clean-db:  ## Clean DB
	@echo "🗄️ Очистка базы данных..."
	rm -f bot.db

restart: clean-db run  ## Перезапуск с чистой БД

deploy:  ## Expand the project
	@echo "🚀 Развертывание..."
	chmod +x deploy.sh
	./deploy.sh

status:  ## show status systemd service
	systemctl status fuel-bot

logs:  ## Show logs
	@echo "📋 Последние логи:"
	@if [ -f "logs/bot.log" ]; then tail -n 50 logs/bot.log; else echo "Логи не найдены"; fi

install-service:  ## Set systemd service
	@echo "⚙️ Установка systemd service..."
	sudo cp fuel-bot.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable fuel-bot
	@echo "✅ Service установлен. Запуск: sudo systemctl start fuel-bot"

# Alias for Windows (if make unavailable)
win-install:  ## Windows: set dependencies
	python fix_dependencies.py

win-setup:  ## Windows: set project
	python setup.py

win-test:  ## Windows: launch tests
	python test_bot.py

win-run:  ## Windows: launch a bot
	python main.py
