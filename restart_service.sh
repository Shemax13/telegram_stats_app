#!/bin/bash

echo "🔄 Перезапуск Telegram сервиса..."

# Остановка существующих процессов
echo "⏹️  Остановка существующих процессов..."
pkill -f "streamlit\|telegram_stats\|telegram_monitor\|run_app.py" 2>/dev/null || true
sleep 2

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
python -c "import streamlit, telethon, pandas, plotly; print('✅ Зависимости OK')" || {
    echo "❌ Ошибка зависимостей. Устанавливаем..."
    pip install telethon python-dotenv streamlit plotly
}

# Запуск основного приложения
echo "🚀 Запуск основного приложения..."
python run_app.py &
MAIN_PID=$!

# Запуск веб-интерфейса
echo "🌐 Запуск веб-интерфейса..."
streamlit run telegram_stats.py --server.port 8501 --server.address 0.0.0.0 &
WEB_PID=$!

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверка статуса
echo "📊 Статус сервисов:"
echo "1. Основное приложение (PID: $MAIN_PID):"
ps -p $MAIN_PID >/dev/null && echo "   ✅ Запущено" || echo "   ❌ Не запущено"

echo "2. Веб-интерфейс (PID: $WEB_PID):"
ps -p $WEB_PID >/dev/null && echo "   ✅ Запущено" || echo "   ❌ Не запущено"

echo "3. Всего Python процессов:"
ps aux | grep python | grep -v grep | wc -l

echo ""
echo "🎉 Сервис перезапущен!"
echo "📱 Веб-интерфейс: http://localhost:8501"
echo "🔧 Для остановки: pkill -f 'streamlit\|telegram_stats\|run_app.py'"