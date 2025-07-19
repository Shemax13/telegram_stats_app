#!/usr/bin/env python3
"""
Тест с использованием существующей сессии
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Загружаем переменные окружения
load_dotenv('telega.env')

async def test_existing_session():
    """Тест с существующей сессией"""
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash}")
    
    try:
        # Используем существующую сессию
        client = TelegramClient('monitor_session', api_id, api_hash)
        
        print("🔗 Подключение с существующей сессией...")
        await client.connect()
        
        if await client.is_user_authorized():
            print("✅ Успешная авторизация с существующей сессией!")
            
            # Получаем информацию о себе
            me = await client.get_me()
            print(f"👤 Авторизован как: {me.first_name} (@{me.username})")
            
            # Тестируем получение канала
            try:
                channel = await client.get_entity("durov")
                print(f"📺 Канал найден: {channel.title}")
                print(f"📊 Участников: {channel.participants_count}")
                
                # Тестируем создание снимка
                from telegram_monitor import TelegramChannelMonitor
                monitor = TelegramChannelMonitor()
                monitor.client = client
                
                print("📸 Создание снимка канала...")
                await monitor.take_snapshot("durov")
                print("✅ Снимок создан успешно!")
                
            except Exception as e:
                print(f"⚠️ Ошибка при работе с каналом: {e}")
            
        else:
            print("❌ Сессия недействительна")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        if 'client' in locals():
            await client.disconnect()
            print("🔌 Соединение закрыто")

if __name__ == "__main__":
    print("🧪 Тест с существующей сессией...")
    asyncio.run(test_existing_session()) 