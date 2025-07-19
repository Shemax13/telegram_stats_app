# 🚀 Быстрый старт

## Установка и запуск за 5 минут

### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

### 2. Получите Telegram API credentials
- Перейдите на https://my.telegram.org/apps
- Войдите в свой аккаунт
- Создайте приложение
- Скопируйте `api_id` и `api_hash`

### 3. Создайте файл .env
```env
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
TELEGRAM_PHONE=+7xxxxxxxxxx
```

### 4. Запустите приложение
```bash
python run_app.py
```

Или напрямую:
```bash
streamlit run telegram_stats.py
```

### 5. Откройте браузер
Перейдите по адресу: http://localhost:8501

## Основные функции

- **Сбор данных**: Введите username канала и нажмите "Собрать данные"
- **Анализ**: Выберите период и нажмите "Показать статистику"
- **Мониторинг**: Запустите `telegram_monitor.py` для отслеживания в реальном времени

## Примеры использования

### Анализ канала
1. Введите username канала (без @)
2. Выберите период анализа
3. Соберите данные
4. Просмотрите графики и статистику

### Мониторинг изменений
1. Откройте `telegram_monitor.py`
2. Добавьте каналы в список `channels_to_monitor`
3. Запустите мониторинг
4. Отслеживайте изменения в консоли

## Экспорт данных

```python
from export_data import DataExporter

exporter = DataExporter()
exporter.export_members_to_csv("channel_name")
exporter.export_stats_to_json("channel_name")
exporter.create_summary_report("channel_name")
```

## Устранение проблем

- **Ошибка авторизации**: Проверьте правильность API credentials
- **Нет доступа к каналу**: Убедитесь, что вы участник канала
- **Ошибки зависимостей**: Переустановите requirements.txt 