# telegram_notifier.py
import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""
    
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        
    async def send_message(self, text: str, parse_mode: str = 'HTML'):
        """Отправка сообщения"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info("✅ Уведомление отправлено в Telegram")
            return True
        except TelegramError as e:
            logger.error(f"❌ Ошибка отправки в Telegram: {e}")
            return False
    
    async def send_trade_notification(self, trade_data: dict):
        """Отправка уведомления о сделке"""
        profit = trade_data.get('actual_profit', 0)
        symbol = trade_data.get('symbol', 'Unknown')
        route = f"{trade_data.get('buy_exchange', '?')} → {trade_data.get('sell_exchange', '?')}"
        
        if profit > 0:
            emoji = "✅"
        else:
            emoji = "❌"
        
        message = f"""
{emoji} <b>НОВАЯ СДЕЛКА</b>

📊 <b>{symbol}</b>
🔄 Маршрут: {route}
💰 Прибыль: <b>${profit:.2f}</b>
⏱️ Время: {trade_data.get('timestamp', '')}
        """
        
        await self.send_message(message)
    
    async def send_daily_stats(self, stats: dict):
        """Отправка дневной статистики"""
        message = f"""
📊 <b>ДНЕВНАЯ СТАТИСТИКА</b>

📈 Сделок: {stats.get('trades', 0)}
💰 Прибыль: <b>${stats.get('profit', 0):.2f}</b>
🎯 Win Rate: {stats.get('win_rate', 0)}%
⏱️ Среднее время: {stats.get('avg_time', 0)} сек

🏆 Лучшая: {stats.get('best_trade', '—')}
📉 Худшая: {stats.get('worst_trade', '—')}
        """
        await self.send_message(message)
    
    async def send_error(self, error: str):
        """Отправка ошибки"""
        message = f"""
⚠️ <b>ОШИБКА БОТА</b>

{error}
        """
        await self.send_message(message)
