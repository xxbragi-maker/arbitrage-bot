#!/bin/bash
# deploy.sh - Скрипт для автоматического развертывания

echo "🚀 Начинаем развертывание ArbitrageX Bot..."

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}❌ Пожалуйста, запустите с sudo${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Права root подтверждены${NC}"

# Обновление системы
echo "📦 Обновление пакетов..."
apt update && apt upgrade -y

# Установка зависимостей
echo "📦 Установка Python и pip..."
apt install -y python3 python3-pip python3-venv git

# Определяем директорию
BOT_DIR="/opt/arbitrage-bot"

# Проверяем, откуда запущен скрипт
if [ -f "main.py" ]; then
    # Скрипт запущен из папки с ботом
    echo "📁 Копируем файлы из текущей директории..."
    mkdir -p $BOT_DIR
    cp -r * $BOT_DIR/
    cd $BOT_DIR
else
    # Скрипт запущен из другого места, переходим в директорию бота
    echo "📁 Переходим в директорию бота..."
    cd $BOT_DIR 2>/dev/null || {
        echo "❌ Директория бота не найдена!"
        exit 1
    }
fi

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Настройка прав
echo "🔒 Настройка прав доступа..."
if [ -f ".env" ]; then
    chmod 600 .env
else
    echo "⚠️ Файл .env не найден, создаем из примера"
    cp .env.example .env
    chmod 600 .env
    echo "📝 Не забудьте отредактировать .env файл!"
fi

chmod +x main.py

# Создание systemd сервиса
echo "⚙️ Настройка автозапуска..."

cat > /etc/systemd/system/arbitrage-bot.service << 'SERVICE'
[Unit]
Description=ArbitrageX Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/arbitrage-bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/arbitrage-bot/venv/bin/python /opt/arbitrage-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable arbitrage-bot

# Запуск бота
echo "🚀 Запуск бота..."
systemctl start arbitrage-bot

# Проверка статуса
echo "📊 Проверка статуса..."
sleep 3
systemctl status arbitrage-bot --no-pager

echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo "📝 Полезные команды:"
echo "   Просмотр логов: journalctl -u arbitrage-bot -f"
echo "   Перезапуск: systemctl restart arbitrage-bot"
echo "   Остановка: systemctl stop arbitrage-bot"
echo ""
echo "📁 Файлы бота находятся в: /opt/arbitrage-bot"
echo "🔧 Отредактируйте .env файл: nano /opt/arbitrage-bot/.env"
