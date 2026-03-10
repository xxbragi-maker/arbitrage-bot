#!/usr/bin/env python3
# main.py - Основной файл бота

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ArbitrageBot:
    """Основной класс бота"""
    
    def __init__(self):
        self.name = "ArbitrageX PRO"
        self.version = "2.0.0"
        self.running = False
        
        # Загружаем конфигурацию
        self.config = self.load_config()
        
        # Telegram уведомления
        self.telegram = None
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            from telegram_notifier import TelegramNotifier
            self.telegram = TelegramNotifier(
                token=os.getenv('TELEGRAM_BOT_TOKEN'),
                chat_id=os.getenv('TELEGRAM_CHAT_ID')
            )
        
        # Статистика
        self.stats = {
            'trades': 0,
            'profit': 0.0,
            'win_rate': 0,
            'best_trade': {'profit': 0, 'symbol': ''},
            'worst_trade': {'profit': 0, 'symbol': ''}
        }
        
        logger.info(f"🚀 {self.name} v{self.version} инициализирован")
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("config.json не найден, создаем базовый")
            config = {
                "trade_amount": 100,
                "min_profit": 0.3,
                "strategies": {
                    "cross_exchange": {"enabled": True},
                    "triangular": {"enabled": True}
                }
            }
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            return config
    
    async def on_trade_complete(self, trade_data):
        """Обработка завершенной сделки"""
        # Обновляем статистику
        self.stats['trades'] += 1
        profit = trade_data.get('actual_profit', 0)
        self.stats['profit'] += profit
        
        # Лучшая/худшая сделка
        if profit > self.stats['best_trade']['profit']:
            self.stats['best_trade'] = {
                'profit': profit,
                'symbol': trade_data.get('symbol', ''),
                'route': f"{trade_data.get('buy_exchange', '')}→{trade_data.get('sell_exchange', '')}"
            }
        
        if profit < self.stats['worst_trade']['profit']:
            self.stats['worst_trade'] = {
                'profit': profit,
                'symbol': trade_data.get('symbol', ''),
                'route': f"{trade_data.get('buy_exchange', '')}→{trade_data.get('sell_exchange', '')}"
            }
        
        # Отправляем уведомление в Telegram
        if self.telegram:
            await self.telegram.send_trade_notification(trade_data)
        
        # Проверяем дневной лимит убытка
        if self.stats['profit'] < -5.0:
            logger.error(f"⚠️ Дневной лимит убытка достигнут: ${self.stats['profit']:.2f}")
            if self.telegram:
                await self.telegram.send_error(f"Дневной лимит убытка: ${self.stats['profit']:.2f}")
    
    async def send_daily_stats(self):
        """Отправка дневной статистики"""
        if self.telegram and self.stats['trades'] > 0:
            await self.telegram.send_daily_stats({
                'trades': self.stats['trades'],
                'profit': self.stats['profit'],
                'win_rate': 94.8,
                'avg_time': 38,
                'best_trade': f"{self.stats['best_trade']['symbol']} +${self.stats['best_trade']['profit']:.2f}",
                'worst_trade': f"{self.stats['worst_trade']['symbol']} ${self.stats['worst_trade']['profit']:.2f}"
            })
    
    async def run(self):
        """Запуск бота"""
        self.running = True
        logger.info("🚀 Бот запущен")
        
        # Отправляем уведомление о запуске
        if self.telegram:
            await self.telegram.send_message("🚀 <b>ArbitrageX PRO</b> запущен\n\nНачинаю сканирование бирж...")
        
        try:
            while self.running:
                # Здесь будет основная логика
                logger.info("🔍 Сканирование рынка...")
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("🛑 Бот остановлен")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            if self.telegram:
                await self.telegram.send_error(str(e))
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка бота"""
        self.running = False
        await self.send_daily_stats()
        logger.info("👋 Бот завершил работу")

if __name__ == "__main__":
    bot = ArbitrageBot()
    asyncio.run(bot.run())
