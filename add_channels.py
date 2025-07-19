#!/usr/bin/env python3
"""
Скрипт для добавления каналов для мониторинга
"""

import asyncio
import os
from dotenv import load_dotenv
from telegram_monitor import TelegramChannelMonitor

# Загружаем переменные окружения
load_dotenv('telega.env')

async def add_channels():
    """Добавление каналов для мониторинга"""
    
    # Список каналов для добавления
    channels_to_add = [
        "shemaxpoetry",    # SheMax Poetry - ваш канал
        "durov",           # Канал Павла Дурова
        "telegram",        # Официальный канал Telegram
        "python_telegram", # Python Telegram Bot
        # Добавьте свои каналы здесь:
        # "your_channel_name",
        # "another_channel_name"
    ]
    
    print("📺 Каналы для мониторинга:")
    for i, channel in enumerate(channels_to_add, 1):
        print(f"  {i}. @{channel}")
    
    # Создаем монитор
    monitor = TelegramChannelMonitor()
    
    try:
        # Подключаемся к Telegram
        print("\n🔗 Подключение к Telegram...")
        await monitor.connect()
        
        # Создаем снимки для каждого канала
        for channel in channels_to_add:
            try:
                print(f"\n📸 Создание снимка канала @{channel}...")
                await monitor.take_snapshot(channel)
                print(f"✅ Снимок канала @{channel} создан")
            except Exception as e:
                print(f"❌ Ошибка при создании снимка @{channel}: {e}")
        
        print(f"\n✅ Обработано {len(channels_to_add)} каналов")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        await monitor.close()
        print("\n🔌 Соединение закрыто")

def show_usage_examples():
    """Показывает примеры использования"""
    
    print("\n📖 Примеры использования:")
    print("\n1. Мониторинг в реальном времени:")
    print("""
import asyncio
from telegram_monitor import TelegramChannelMonitor

async def main():
    monitor = TelegramChannelMonitor()
    channels = ["durov", "telegram"]
    
    try:
        await monitor.start_monitoring(channels)
    except KeyboardInterrupt:
        print("Мониторинг остановлен")
    finally:
        await monitor.close()

asyncio.run(main())
""")
    
    print("\n2. Получение статистики:")
    print("""
from telegram_monitor import TelegramChannelMonitor

monitor = TelegramChannelMonitor()
stats = monitor.get_channel_statistics("durov", days=30)
print(f"Подписчиков: {stats['joined_count']}")
print(f"Отписалось: {stats['left_count']}")
""")
    
    print("\n3. Экспорт данных:")
    print("""
from telegram_monitor import TelegramChannelMonitor

monitor = TelegramChannelMonitor()
monitor.export_data_to_csv("durov", "durov_data.csv")
""")

if __name__ == "__main__":
    print("🚀 Добавление каналов для мониторинга...")
    
    # Показываем примеры
    show_usage_examples()
    
    # Спрашиваем пользователя
    response = input("\nХотите добавить каналы сейчас? (y/n): ")
    
    if response.lower() in ['y', 'yes', 'да', 'д']:
        asyncio.run(add_channels())
    else:
        print("\nДля добавления каналов запустите скрипт снова или используйте примеры выше.") 