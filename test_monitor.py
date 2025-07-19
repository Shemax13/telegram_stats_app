#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Telegram монитора
"""

import asyncio
import os
from dotenv import load_dotenv
from telegram_monitor import TelegramChannelMonitor

# Загружаем переменные из telega.env
load_dotenv('telega.env')

async def test_monitor():
    """Тестирование основных функций монитора"""
    
    # Проверяем наличие переменных окружения
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Отсутствуют необходимые переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nСоздайте файл .env на основе env_example.txt и заполните необходимые данные")
        return
    
    print("✅ Все переменные окружения настроены")
    
    # Создаем экземпляр монитора
    monitor = TelegramChannelMonitor()
    
    try:
        # Тестируем подключение
        print("\n🔗 Тестирование подключения к Telegram API...")
        await monitor.connect()
        print("✅ Подключение к Telegram API успешно")
        
        # Тестируем создание снимка (замените на реальный канал)
        test_channel = "durov"  # Пример канала
        
        print(f"\n📸 Тестирование создания снимка канала {test_channel}...")
        try:
            await monitor.take_snapshot(test_channel)
            print("✅ Снимок создан успешно")
        except Exception as e:
            print(f"⚠️  Ошибка при создании снимка: {e}")
        
        # Тестируем получение статистики
        print(f"\n📊 Тестирование получения статистики канала {test_channel}...")
        try:
            stats = monitor.get_channel_statistics(test_channel, days=7)
            print("✅ Статистика получена:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"⚠️  Ошибка при получении статистики: {e}")
        
        # Тестируем экспорт данных
        print(f"\n📁 Тестирование экспорта данных канала {test_channel}...")
        try:
            monitor.export_data_to_csv(test_channel)
            print("✅ Экспорт данных выполнен")
        except Exception as e:
            print(f"⚠️  Ошибка при экспорте данных: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    finally:
        await monitor.close()
        print("\n🔌 Соединение закрыто")

def test_database():
    """Тестирование базы данных"""
    print("\n🗄️  Тестирование базы данных...")
    
    monitor = TelegramChannelMonitor()
    
    try:
        # Проверяем, что таблицы созданы
        import sqlite3
        conn = sqlite3.connect(monitor.db_path)
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("✅ Таблицы в базе данных:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании базы данных: {e}")

if __name__ == "__main__":
    print("🧪 Запуск тестирования Telegram монитора...")
    
    # Тестируем базу данных
    test_database()
    
    # Тестируем основной функционал
    asyncio.run(test_monitor())
    
    print("\n✅ Тестирование завершено") 