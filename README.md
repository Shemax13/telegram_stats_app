# ChannelStat - Telegram Channel Monitor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Telethon](https://img.shields.io/badge/Telethon-1.40.0+-green.svg)](https://docs.telethon.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Инструмент для мониторинга изменений в Telegram каналах в реальном времени. Отслеживает подписки и отписки пользователей, создает снимки состояния каналов и предоставляет аналитику роста.

## 🚀 Возможности

- **Мониторинг в реальном времени** - отслеживание подписок и отписок
- **Создание снимков** - фиксация текущего состояния каналов
- **Статистика роста** - анализ динамики изменения количества участников
- **Экспорт данных** - выгрузка в CSV для дальнейшего анализа
- **Множественные каналы** - одновременный мониторинг нескольких каналов

## 📋 Требования

- Python 3.8+
- Telegram API ключи
- Интернет-соединение

## 🛠️ Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Shemax13/telegram_stats_app.git
   cd telegram_stats_app
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте Telegram API:**
   - Перейдите на https://my.telegram.org/apps
   - Создайте новое приложение
   - Скопируйте `api_id` и `api_hash`

4. **Создайте файл конфигурации:**
   ```bash
   cp env_example.txt telega.env
   ```
   
   Отредактируйте `telega.env` и добавьте ваши данные:
   ```env
   TELEGRAM_API_ID=your_api_id_here
   TELEGRAM_API_HASH=your_api_hash_here
   TELEGRAM_PHONE=+7xxxxxxxxxx
   ```

## 🚀 Быстрый старт

### Тестирование
```bash
python test_monitor.py
```

### Мониторинг каналов
```python
import asyncio
from telegram_monitor import TelegramChannelMonitor

async def main():
    monitor = TelegramChannelMonitor()
    channels = ["channel1", "channel2"]
    
    try:
        await monitor.start_monitoring(channels)
    except KeyboardInterrupt:
        print("Мониторинг остановлен")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Использование

### Создание снимка канала
```python
await monitor.take_snapshot("channel_username")
```

### Получение статистики
```python
stats = monitor.get_channel_statistics("channel_username", days=30)
print(f"Подписчиков: {stats['joined_count']}")
print(f"Отписалось: {stats['left_count']}")
```

### Экспорт данных
```python
monitor.export_data_to_csv("channel_username", "output.csv")
```

## 📁 Структура проекта

```
telegram_stats_app/
├── telegram_monitor.py      # Основной модуль мониторинга
├── telegram_stats.py        # Модуль статистики
├── run_app.py              # Веб-интерфейс
├── export_data.py          # Экспорт данных
├── test_monitor.py         # Тестовый скрипт
├── requirements.txt        # Зависимости
├── telega.env             # Конфигурация (не в репозитории)
├── README.md              # Документация
├── MONITOR_USAGE.md       # Подробное руководство
└── QUICK_START.md         # Быстрый старт
```

## 🔧 API Reference

### TelegramChannelMonitor

Основной класс для мониторинга каналов.

#### Методы:
- `connect()` - Подключение к Telegram API
- `start_monitoring(channels)` - Запуск мониторинга
- `take_snapshot(channel)` - Создание снимка
- `get_channel_statistics(channel, days)` - Получение статистики
- `export_data_to_csv(channel, file)` - Экспорт данных

## 📈 Примеры

### Мониторинг популярных каналов
```python
channels = [
    "durov",
    "telegram",
    "python_telegram"
]
await monitor.start_monitoring(channels)
```

### Анализ роста канала
```python
trend = monitor.get_growth_trend("channel_username", days=7)
for _, row in trend.iterrows():
    print(f"Дата: {row['date']}, Участников: {row['avg_members']}")
```

## 🛡️ Безопасность

- Файл `telega.env` с API ключами не загружается в репозиторий
- Все данные хранятся локально в SQLite базе
- Поддерживается безопасная авторизация через Telegram

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## ⚠️ Отказ от ответственности

Этот инструмент предназначен только для образовательных целей. Убедитесь, что вы соблюдаете условия использования Telegram API и не нарушаете права других пользователей.

## 📞 Поддержка

Если у вас есть вопросы или предложения, создайте Issue в репозитории.

---

**Автор:** [@Shemax13](https://github.com/Shemax13)

**Версия:** 1.0.0 