#!/usr/bin/env python3
"""
Простой тест подключения к Telegram
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Загружаем переменные окружения
load_dotenv('telega.env')

async def simple_test():
    """Простой тест подключения"""
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash}")
    print(f"Phone: {phone}")
    
    if not all([api_id, api_hash, phone]):
        print("❌ Не все переменные окружения настроены")
        return
    
    try:
        # Создаем клиент
        client = TelegramClient('test_session', api_id, api_hash)
        
        print("🔗 Подключение к Telegram...")
        await client.start(phone=phone)
        
        if await client.is_user_authorized():
            print("✅ Успешная авторизация!")
            
            # Получаем информацию о себе
            me = await client.get_me()
            print(f"👤 Авторизован как: {me.first_name} (@{me.username})")
            
            # Тестируем получение канала
            try:
                channel = await client.get_entity("durov")
                print(f"📺 Канал найден: {channel.title}")
                print(f"📊 Участников: {channel.participants_count}")
            except Exception as e:
                print(f"⚠️ Ошибка при получении канала: {e}")
            
        else:
            print("❌ Не удалось авторизоваться")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        if 'client' in locals():
            await client.disconnect()
            print("🔌 Соединение закрыто")

if __name__ == "__main__":
    print("🧪 Простой тест подключения к Telegram...")
    asyncio.run(simple_test()) 