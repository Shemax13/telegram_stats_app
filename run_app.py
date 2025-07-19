#!/usr/bin/env python3
"""
Скрипт для запуска приложения статистики Telegram каналов
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    print(f"✅ Python версия: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = [
        'telethon',
        'python-dotenv',
        'pandas',
        'streamlit',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} установлен")
    
    if missing_packages:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Проверка наличия файла .env"""
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден")
        print("Создайте файл .env со следующими переменными:")
        print("TELEGRAM_API_ID=ваш_api_id")
        print("TELEGRAM_API_HASH=ваш_api_hash")
        print("TELEGRAM_PHONE=+7xxxxxxxxxx")
        return False
    
    print("✅ Файл .env найден")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")
        return False

def run_streamlit():
    """Запуск Streamlit приложения"""
    print("🚀 Запуск веб-приложения...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'telegram_stats.py'])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")

def run_monitor():
    """Запуск мониторинга в реальном времени"""
    print("🔍 Запуск мониторинга в реальном времени...")
    try:
        subprocess.run([sys.executable, 'telegram_monitor.py'])
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен")

def show_menu():
    """Показать меню выбора"""
    print("\n" + "="*50)
    print("📊 TELEGRAM CHANNEL STATISTICS")
    print("="*50)
    print("1. 🌐 Запустить веб-приложение")
    print("2. 🔍 Запустить мониторинг в реальном времени")
    print("3. 📦 Установить зависимости")
    print("4. ✅ Проверить настройки")
    print("5. 📖 Показать справку")
    print("0. 🚪 Выход")
    print("="*50)

def show_help():
    """Показать справку"""
    print("\n📖 СПРАВКА")
    print("-" * 30)
    print("1. Получите API credentials на https://my.telegram.org/apps")
    print("2. Создайте файл .env с вашими данными")
    print("3. Установите зависимости: pip install -r requirements.txt")
    print("4. Запустите веб-приложение для анализа")
    print("5. Используйте мониторинг для отслеживания в реальном времени")
    print("\n📁 Файлы проекта:")
    print("- telegram_stats.py - основное веб-приложение")
    print("- telegram_monitor.py - мониторинг в реальном времени")
    print("- export_data.py - экспорт данных")
    print("- requirements.txt - зависимости")
    print("- README.md - подробная документация")

def main():
    """Основная функция"""
    print("🔍 Проверка системы...")
    
    # Проверка версии Python
    if not check_python_version():
        return
    
    # Проверка зависимостей
    if not check_dependencies():
        print("\nХотите установить зависимости? (y/n): ", end="")
        if input().lower() == 'y':
            if not install_dependencies():
                return
        else:
            return
    
    # Проверка файла .env
    if not check_env_file():
        print("\nСоздайте файл .env перед запуском приложения")
        return
    
    # Основной цикл меню
    while True:
        show_menu()
        choice = input("\nВыберите действие (0-5): ").strip()
        
        if choice == '1':
            run_streamlit()
        elif choice == '2':
            run_monitor()
        elif choice == '3':
            install_dependencies()
        elif choice == '4':
            print("\n🔍 ПРОВЕРКА НАСТРОЕК")
            print("-" * 20)
            check_python_version()
            check_dependencies()
            check_env_file()
        elif choice == '5':
            show_help()
        elif choice == '0':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main() 