@echo off
REM Batch file with commands for Windows

if "%1"=="install" goto install
if "%1"=="setup" goto setup
if "%1"=="test" goto test
if "%1"=="run" goto run
if "%1"=="get-id" goto get-id
if "%1"=="clean" goto clean
if "%1"=="help" goto help

:help
echo 🤖 Fuel Talon Bot - Команды для Windows
echo =====================================
echo.
echo commands install  - Установить зависимости
echo commands setup    - Настроить проект
echo commands test     - Запустить тесты
echo commands run      - Запустить бота
echo commands get-id   - Получить Telegram ID
echo commands clean    - Очистить временные файлы
echo.
goto end

:install
echo 📦 Установка зависимостей...
python fix_dependencies.py
goto end

:setup
echo ⚙️ Настройка проекта...
python setup.py
goto end

:test
echo 🧪 Запуск тестов...
python test_bot.py
goto end

:run
echo 🚀 Запуск бота...
python main.py
goto end

:get-id
echo 🆔 Получение Telegram ID...
python get_my_id.py
goto end

:clean
echo 🧹 Очистка...
if exist __pycache__ rmdir /s /q __pycache__
if exist handlers\__pycache__ rmdir /s /q handlers\__pycache__
if exist keyboards\__pycache__ rmdir /s /q keyboards\__pycache__
if exist utils\__pycache__ rmdir /s /q utils\__pycache__
if exist logs\*.log del /q logs\*.log
if exist qr_codes\*.png del /q qr_codes\*.png
echo ✅ Очистка завершена
goto end

:end
