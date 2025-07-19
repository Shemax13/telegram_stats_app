# Telegram Channel Monitor - Руководство по использованию

## Описание

Telegram Channel Monitor - это инструмент для мониторинга изменений в Telegram каналах в реальном времени. Он отслеживает подписки и отписки пользователей, создает снимки состояния каналов и предоставляет статистику.

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка Telegram API

1. Перейдите на https://my.telegram.org/apps
2. Войдите в свой аккаунт Telegram
3. Создайте новое приложение со следующими параметрами:

   **App title:** `ChannelStat`
   
   **Short name:** `CHStat` (5-32 символа, буквенно-цифровые)
   
   **URL:** `https://github.com/Shemax13/telegram_stats_app` (или оставьте пустым)
   
   **Platform:** `Desktop`
   
   **Description:** `ChannelStat - инструмент для мониторинга статистики Telegram каналов в реальном времени. Отслеживает подписки и отписки пользователей, создает снимки состояния каналов и предоставляет аналитику роста.`

4. После создания приложения скопируйте `api_id` и `api_hash`

### 3. Создание файла telega.env

Создайте файл `telega.env` в корневой папке проекта:

```env
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+7xxxxxxxxxx
```

Замените значения на ваши реальные данные:

- `your_api_id_here` → ваш числовой `api_id`
- `your_api_hash_here` → ваш строковый `api_hash` 
- `+7xxxxxxxxxx` → ваш номер телефона в международном формате

**Пример:**
```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+79001234567
```

### 4. Проверка настройки

После заполнения файла `telega.env` запустите тестовый скрипт:

```bash
python test_monitor.py
```

Если все настроено правильно, вы увидите:
- ✅ Все переменные окружения настроены
- ✅ Подключение к Telegram API успешно
- ✅ Снимок создан успешно
- ✅ Статистика получена

При первом запуске потребуется ввести код подтверждения из Telegram.

## Использование

### Базовое использование

```python
import asyncio
from telegram_monitor import TelegramChannelMonitor

async def main():
    monitor = TelegramChannelMonitor()
    
    # Список каналов для мониторинга
    channels = ["channel1", "channel2", "channel3"]
    
    try:
        await monitor.start_monitoring(channels)
    except KeyboardInterrupt:
        print("Мониторинг остановлен")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Создание снимка канала

```python
async def take_snapshot():
    monitor = TelegramChannelMonitor()
    await monitor.connect()
    
    # Создаем снимок канала
    await monitor.take_snapshot("channel_username")
    
    await monitor.close()
```

### Получение статистики

```python
def get_stats():
    monitor = TelegramChannelMonitor()
    
    # Получаем статистику за последние 30 дней
    stats = monitor.get_channel_statistics("channel_username", days=30)
    
    print(f"Подписчиков: {stats['joined_count']}")
    print(f"Отписалось: {stats['left_count']}")
    print(f"Чистый рост: {stats['net_growth']}")
    print(f"Текущее количество: {stats['current_members']}")
```

### Экспорт данных

```python
def export_data():
    monitor = TelegramChannelMonitor()
    
    # Экспортируем данные в CSV файл
    monitor.export_data_to_csv("channel_username", "output.csv")
```

## API Reference

### TelegramChannelMonitor

#### Методы

- `__init__()` - Инициализация монитора
- `async connect()` - Подключение к Telegram API
- `async start_monitoring(channels)` - Запуск мониторинга каналов
- `async take_snapshot(channel_username)` - Создание снимка канала
- `get_recent_changes(channel_username, hours=24)` - Получение недавних изменений
- `get_growth_trend(channel_username, days=7)` - Получение тренда роста
- `get_channel_statistics(channel_username, days=30)` - Получение статистики
- `export_data_to_csv(channel_username, output_file)` - Экспорт данных
- `async close()` - Закрытие соединения

## Структура базы данных

### Таблица `real_time_changes`

Хранит изменения в реальном времени:

- `id` - Уникальный идентификатор
- `channel_id` - ID канала
- `user_id` - ID пользователя
- `change_type` - Тип изменения ('joined' или 'left')
- `change_date` - Дата изменения
- `username` - Username пользователя
- `first_name` - Имя пользователя
- `last_name` - Фамилия пользователя
- `created_at` - Дата создания записи

### Таблица `channel_snapshots`

Хранит снимки состояния каналов:

- `id` - Уникальный идентификатор
- `channel_id` - ID канала
- `channel_username` - Username канала
- `member_count` - Количество участников
- `snapshot_date` - Дата снимка
- `created_at` - Дата создания записи

## Примеры использования

### Мониторинг нескольких каналов

```python
async def monitor_multiple_channels():
    monitor = TelegramChannelMonitor()
    
    channels = [
        "durov",
        "telegram",
        "python_telegram"
    ]
    
    await monitor.start_monitoring(channels)
```

### Анализ роста канала

```python
def analyze_growth():
    monitor = TelegramChannelMonitor()
    
    # Получаем тренд за последние 7 дней
    trend = monitor.get_growth_trend("channel_username", days=7)
    
    print("Тренд роста канала:")
    for _, row in trend.iterrows():
        print(f"Дата: {row['date']}, Среднее: {row['avg_members']}")
```

### Экспорт данных для анализа

```python
def export_for_analysis():
    monitor = TelegramChannelMonitor()
    
    # Экспортируем данные за последние 30 дней
    monitor.export_data_to_csv("channel_username", "analysis_data.csv")
    
    # Получаем статистику
    stats = monitor.get_channel_statistics("channel_username", days=30)
    
    print(f"Статистика за 30 дней:")
    print(f"Новых подписчиков: {stats['joined_count']}")
    print(f"Отписалось: {stats['left_count']}")
    print(f"Чистый рост: {stats['net_growth']}")
```

## Тестирование

Запустите тестовый скрипт для проверки работы:

```bash
python test_monitor.py
```

Этот скрипт проверит:
- Настройку переменных окружения
- Подключение к Telegram API
- Создание снимков
- Получение статистики
- Экспорт данных

## Примечания

1. **Ограничения API**: Telegram API имеет ограничения на количество запросов. Не превышайте лимиты.

2. **Приватные каналы**: Для мониторинга приватных каналов необходимо быть их участником.

3. **Авторизация**: При первом запуске потребуется ввести код подтверждения из Telegram.

4. **Хранение данных**: Все данные сохраняются в локальной SQLite базе данных.

## Устранение неполадок

### Ошибка авторизации

```
ValueError: Необходимо указать TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE в .env файле
```

Решение: Проверьте, что файл `telega.env` создан и содержит правильные данные.

### Ошибка подключения

```
ConnectionError: Не удается подключиться к Telegram
```

Решение: Проверьте интернет-соединение и правильность API ключей.

### Канал не найден

```
ChannelNotFoundError: Канал не найден
```

Решение: Проверьте правильность username канала и убедитесь, что канал публичный или вы являетесь его участником. 