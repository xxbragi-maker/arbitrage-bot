#!/bin/bash
# deploy.sh - Полная автоматическая установка бота + веб-интерфейса

set -e  # Прерывать при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🚀 ArbitrageX PRO - Автоматическая установка${NC}"
echo -e "${BLUE}========================================${NC}"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Пожалуйста, запустите с sudo${NC}"
    exit 1
fi

# Определяем директорию установки
INSTALL_DIR="/opt/arbitrage-bot"
echo -e "${YELLOW}📁 Директория установки: $INSTALL_DIR${NC}"

# Создаем директорию
mkdir -p $INSTALL_DIR

# Копируем файлы (если запущено из папки с репозиторием)
if [ -f "main.py" ]; then
    echo -e "${GREEN}✅ Копируем файлы из текущей директории...${NC}"
    cp -r * $INSTALL_DIR/
else
    echo -e "${YELLOW}⚠️ Файлы не найдены, клонируем репозиторий...${NC}"
    cd $INSTALL_DIR
    if [ ! -d ".git" ]; then
        git clone https://github.com/ВАШ_USERNAME/arbitrage-bot.git .
    else
        git pull
    fi
fi

cd $INSTALL_DIR

# Обновление системы
echo -e "${YELLOW}📦 Обновление пакетов...${NC}"
apt update && apt upgrade -y

# Установка зависимостей
echo -e "${YELLOW}📦 Установка Python и необходимых пакетов...${NC}"
apt install -y python3-pip python3-venv git curl wget ufw

# Создание виртуального окружения
echo -e "${YELLOW}🐍 Создание виртуального окружения...${NC}"
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
echo -e "${YELLOW}📦 Установка Python зависимостей...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Настройка прав
echo -e "${YELLOW}🔒 Настройка прав доступа...${NC}"
if [ -f ".env" ]; then
    chmod 600 .env
else
    cp .env.example .env
    chmod 600 .env
    echo -e "${RED}⚠️  ВНИМАНИЕ: Отредактируйте файл .env!${NC}"
    echo -e "   nano $INSTALL_DIR/.env"
fi

chmod +x main.py web_dashboard.py

# Создание systemd сервиса для бота
echo -e "${YELLOW}⚙️ Настройка автозапуска бота...${NC}"

cat > /etc/systemd/system/arbitrage-bot.service << 'EOF'
[Unit]
Description=ArbitrageX Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/arbitrage-bot
Environment=PATH=/opt/arbitrage-bot/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/arbitrage-bot/venv/bin/python /opt/arbitrage-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Создание systemd сервиса для веб-интерфейса
echo -e "${YELLOW}⚙️ Настройка автозапуска веб-интерфейса...${NC}"

cat > /etc/systemd/system/arbitrage-web.service << 'EOF'
[Unit]
Description=ArbitrageX Web Dashboard
After=network.target arbitrage-bot.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/arbitrage-bot
Environment=PATH=/opt/arbitrage-bot/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/opt/arbitrage-bot/venv/bin/python /opt/arbitrage-bot/web_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
systemctl daemon-reload

# Включение и запуск сервисов
echo -e "${YELLOW}🚀 Запуск сервисов...${NC}"
systemctl enable arbitrage-bot
systemctl enable arbitrage-web
systemctl start arbitrage-bot
systemctl start arbitrage-web

# Настройка firewall
echo -e "${YELLOW}🔓 Настройка firewall для порта 8000...${NC}"
ufw allow 8000/tcp
ufw reload

# Проверка статуса
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}📊 ПРОВЕРКА СТАТУСА:${NC}"
echo -e "${BLUE}========================================${NC}"

sleep 3
systemctl status arbitrage-bot --no-pager
systemctl status arbitrage-web --no-pager

# Получение IP адреса
IP_ADDR=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "НЕ УДАЛОСЬ ОПРЕДЕЛИТЬ")

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ УСТАНОВКА ЗАВЕРШЕНА!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e ""
echo -e "${YELLOW}📁 Файлы бота:${NC} $INSTALL_DIR"
echo -e ""
echo -e "${YELLOW}🔧 Для редактирования .env:${NC}"
echo -e "   nano $INSTALL_DIR/.env"
echo -e ""
echo -e "${YELLOW}🌐 ДОСТУП К ВЕБ-ИНТЕРФЕЙСУ:${NC}"
echo -e ""
echo -e "   ${GREEN}Вариант 1: SSH-туннель (безопасно)${NC}"
echo -e "   На вашем компьютере выполните:"
echo -e "   ssh -L 8080:localhost:8000 root@$IP_ADDR"
echo -e "   Затем откройте: ${GREEN}http://localhost:8080${NC}"
echo -e ""
echo -e "   ${GREEN}Вариант 2: Прямой доступ (если нужен)${NC}"
echo -e "   Откройте: ${GREEN}http://$IP_ADDR:8000${NC}"
echo -e ""
echo -e "${YELLOW}📊 Команды для управления:${NC}"
echo -e "   Статус бота:     systemctl status arbitrage-bot"
echo -e "   Логи бота:       journalctl -u arbitrage-bot -f"
echo -e "   Статус веба:     systemctl status arbitrage-web"
echo -e "   Логи веба:       journalctl -u arbitrage-web -f"
echo -e "   Перезапуск:      systemctl restart arbitrage-bot"
echo -e ""
echo -e "${RED}⚠️  ВАЖНО: Отредактируйте .env файл с вашими Telegram ключами!${NC}"
echo -e "${BLUE}========================================${NC}"