import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from telethon import TelegramClient, events
from telethon.tl.types import Channel, User, UpdateChannel
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from dotenv import load_dotenv

load_dotenv('telega.env')

class TelegramChannelMonitor:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.client = None
        self.db_path = 'telegram_stats.db'
        self.monitored_channels = set()
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных для мониторинга"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для отслеживания изменений в реальном времени
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_time_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_id INTEGER,
                change_type TEXT, -- 'joined' или 'left'
                change_date TIMESTAMP,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для хранения последнего состояния каналов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                channel_username TEXT,
                member_count INTEGER,
                snapshot_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def connect(self):
        """Подключение к Telegram API"""
        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError("Необходимо указать TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE в .env файле")
        
        self.client = TelegramClient('monitor_session', self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            code = input('Введите код подтверждения: ')
            await self.client.sign_in(self.phone, code)
    
    async def start_monitoring(self, channel_usernames: List[str]):
        """Начало мониторинга каналов"""
        if not self.client:
            await self.connect()
        
        # Регистрируем обработчики событий
        @self.client.on(events.ChatAction)
        async def handle_chat_action(event):
            if event.chat_id in self.monitored_channels:
                await self.process_chat_action(event)
        
        # Получаем информацию о каналах
        for username in channel_usernames:
            try:
                channel = await self.client.get_entity(username)
                self.monitored_channels.add(channel.id)
                print(f"Начат мониторинг канала: {username}")
            except Exception as e:
                print(f"Ошибка при получении канала {username}: {e}")
        
        # Запускаем мониторинг
        print("Мониторинг запущен. Нажмите Ctrl+C для остановки.")
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            print("\nМониторинг остановлен.")
    
    async def process_chat_action(self, event):
        """Обработка изменений в чате"""
        try:
            # Определяем тип изменения
            if event.user_added:
                change_type = 'joined'
            elif event.user_kicked or event.user_left:
                change_type = 'left'
            else:
                return
            
            # Получаем информацию о пользователе
            user = event.user
            if not user:
                return
            
            # Сохраняем изменение в базу данных
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO real_time_changes 
                (channel_id, user_id, change_type, change_date, username, first_name, last_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.chat_id,
                user.id,
                change_type,
                datetime.now(),
                user.username,
                user.first_name,
                user.last_name
            ))
            
            conn.commit()
            conn.close()
            
            # Выводим информацию об изменении
            action_text = "подписался" if change_type == 'joined' else "отписался"
            user_info = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name or ''}"
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user_info} {action_text}")
            
        except Exception as e:
            print(f"Ошибка при обработке изменения: {e}")
    
    async def take_snapshot(self, channel_username: str):
        """Создание снимка текущего состояния канала"""
        if not self.client:
            await self.connect()
            
        try:
            channel = await self.client.get_entity(channel_username)
            
            # Получаем количество участников
            participants = await self.client(GetParticipantsRequest(
                channel=channel,
                filter=ChannelParticipantsSearch(''),
                offset=0,
                limit=1,
                hash=0
            ))
            
            # Сохраняем снимок
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO channel_snapshots 
                (channel_id, channel_username, member_count, snapshot_date)
                VALUES (?, ?, ?, ?)
            ''', (
                channel.id,
                channel_username,
                participants.count if hasattr(participants, 'count') else 0,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            print(f"Снимок канала {channel_username} создан")
            
        except Exception as e:
            print(f"Ошибка при создании снимка канала {channel_username}: {e}")
    
    def get_recent_changes(self, channel_username: str, hours: int = 24) -> pd.DataFrame:
        """Получение недавних изменений"""
        conn = sqlite3.connect(self.db_path)
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        # Сначала получаем channel_id по username из таблицы snapshots
        query = '''
            SELECT 
                rc.change_type,
                rc.change_date,
                rc.username,
                rc.first_name,
                rc.last_name
            FROM real_time_changes rc
            JOIN channel_snapshots cs ON rc.channel_id = cs.channel_id
            WHERE cs.channel_username = ? AND rc.change_date >= ?
            ORDER BY rc.change_date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[channel_username, since_time])
        conn.close()
        return df
    
    def get_growth_trend(self, channel_username: str, days: int = 7) -> pd.DataFrame:
        """Получение тренда роста канала"""
        conn = sqlite3.connect(self.db_path)
        
        since_time = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT 
                DATE(snapshot_date) as date,
                AVG(member_count) as avg_members,
                MAX(member_count) as max_members,
                MIN(member_count) as min_members
            FROM channel_snapshots
            WHERE channel_username = ? AND snapshot_date >= ?
            GROUP BY DATE(snapshot_date)
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=[channel_username, since_time])
        conn.close()
        return df
    
    def get_channel_statistics(self, channel_username: str, days: int = 30) -> Dict:
        """Получение статистики канала"""
        conn = sqlite3.connect(self.db_path)
        
        since_time = datetime.now() - timedelta(days=days)
        
        # Получаем статистику изменений
        changes_query = '''
            SELECT 
                change_type,
                COUNT(*) as count
            FROM real_time_changes rc
            JOIN channel_snapshots cs ON rc.channel_id = cs.channel_id
            WHERE cs.channel_username = ? AND rc.change_date >= ?
            GROUP BY change_type
        '''
        
        changes_df = pd.read_sql_query(changes_query, conn, params=[channel_username, since_time])
        
        # Получаем последний снимок
        snapshot_query = '''
            SELECT member_count, snapshot_date
            FROM channel_snapshots
            WHERE channel_username = ?
            ORDER BY snapshot_date DESC
            LIMIT 1
        '''
        
        snapshot_df = pd.read_sql_query(snapshot_query, conn, params=[channel_username])
        
        conn.close()
        
        # Формируем статистику
        stats = {
            'channel_username': channel_username,
            'period_days': days,
            'joined_count': 0,
            'left_count': 0,
            'net_growth': 0,
            'current_members': 0,
            'last_snapshot_date': None
        }
        
        if not changes_df.empty:
            for _, row in changes_df.iterrows():
                if row['change_type'] == 'joined':
                    stats['joined_count'] = row['count']
                elif row['change_type'] == 'left':
                    stats['left_count'] = row['count']
            
            stats['net_growth'] = stats['joined_count'] - stats['left_count']
        
        if not snapshot_df.empty:
            stats['current_members'] = snapshot_df.iloc[0]['member_count']
            stats['last_snapshot_date'] = snapshot_df.iloc[0]['snapshot_date']
        
        return stats
    
    def export_data_to_csv(self, channel_username: str, output_file: str = None):
        """Экспорт данных канала в CSV файл"""
        if not output_file:
            output_file = f"{channel_username}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Получаем все изменения
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                rc.change_type,
                rc.change_date,
                rc.username,
                rc.first_name,
                rc.last_name
            FROM real_time_changes rc
            JOIN channel_snapshots cs ON rc.channel_id = cs.channel_id
            WHERE cs.channel_username = ?
            ORDER BY rc.change_date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[channel_username])
        conn.close()
        
        if not df.empty:
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Данные экспортированы в файл: {output_file}")
        else:
            print(f"Нет данных для канала {channel_username}")
    
    async def close(self):
        """Закрытие соединения"""
        if self.client:
            await self.client.disconnect()

async def main():
    """Основная функция для запуска мониторинга"""
    monitor = TelegramChannelMonitor()
    
    # Список каналов для мониторинга
    channels_to_monitor = [
        # Добавьте сюда username каналов для мониторинга
        # "example_channel",
        # "another_channel"
    ]
    
    if not channels_to_monitor:
        print("Добавьте каналы для мониторинга в список channels_to_monitor")
        return
    
    try:
        await monitor.start_monitoring(channels_to_monitor)
    except Exception as e:
        print(f"Ошибка при запуске мониторинга: {e}")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(main()) 