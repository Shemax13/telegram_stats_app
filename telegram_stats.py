import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from telethon import TelegramClient, events
from telethon.tl.types import Channel, User
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class TelegramStatsCollector:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.client = None
        self.db_path = 'telegram_stats.db'
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для хранения участников канала
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_date TIMESTAMP,
                left_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для хранения истории изменений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_id INTEGER,
                change_type TEXT, -- 'joined' или 'left'
                change_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def connect(self):
        """Подключение к Telegram API"""
        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError("Необходимо указать TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE в .env файле")
        
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            code = input('Введите код подтверждения: ')
            await self.client.sign_in(self.phone, code)
    
    async def get_channel_info(self, channel_username: str) -> Optional[Channel]:
        """Получение информации о канале"""
        try:
            channel = await self.client.get_entity(channel_username)
            return channel
        except Exception as e:
            st.error(f"Ошибка при получении информации о канале: {e}")
            return None
    
    async def collect_members(self, channel_username: str):
        """Сбор участников канала"""
        channel = await self.get_channel_info(channel_username)
        if not channel:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Получаем всех участников канала
            participants = []
            offset = 0
            limit = 200
            
            while True:
                participants_chunk = await self.client(GetParticipantsRequest(
                    channel=channel,
                    filter=ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=limit,
                    hash=0
                ))
                
                if not participants_chunk.users:
                    break
                
                participants.extend(participants_chunk.users)
                offset += len(participants_chunk.users)
                
                if len(participants_chunk.users) < limit:
                    break
            
            # Сохраняем участников в базу данных
            current_time = datetime.now()
            for participant in participants:
                cursor.execute('''
                    INSERT OR REPLACE INTO channel_members 
                    (channel_id, user_id, username, first_name, last_name, joined_date, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    channel.id,
                    participant.id,
                    participant.username,
                    participant.first_name,
                    participant.last_name,
                    current_time,
                    1
                ))
            
            conn.commit()
            st.success(f"Собрано {len(participants)} участников канала")
            
        except Exception as e:
            st.error(f"Ошибка при сборе участников: {e}")
        finally:
            conn.close()
    
    def get_member_changes(self, channel_username: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Получение изменений участников за период"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                mc.change_type,
                mc.change_date,
                cm.username,
                cm.first_name,
                cm.last_name
            FROM member_changes mc
            JOIN channel_members cm ON mc.user_id = cm.user_id
            WHERE mc.change_date BETWEEN ? AND ?
            ORDER BY mc.change_date
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        return df
    
    def get_current_stats(self, channel_username: str) -> Dict:
        """Получение текущей статистики канала"""
        conn = sqlite3.connect(self.db_path)
        
        # Общее количество участников
        total_members = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM channel_members WHERE is_active = 1', 
            conn
        ).iloc[0]['count']
        
        # Участники за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_members = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM channel_members WHERE joined_date >= ? AND is_active = 1',
            conn,
            params=[thirty_days_ago]
        ).iloc[0]['count']
        
        # Участники, покинувшие за последние 30 дней
        left_members = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM member_changes WHERE change_type = "left" AND change_date >= ?',
            conn,
            params=[thirty_days_ago]
        ).iloc[0]['count']
        
        conn.close()
        
        return {
            'total_members': total_members,
            'new_members_30d': new_members,
            'left_members_30d': left_members,
            'net_growth_30d': new_members - left_members
        }
    
    def create_visualizations(self, channel_username: str, start_date: datetime, end_date: datetime):
        """Создание визуализаций статистики"""
        df = self.get_member_changes(channel_username, start_date, end_date)
        
        if df.empty:
            st.warning("Нет данных для отображения за выбранный период")
            return
        
        # График изменений по дням
        df['date'] = pd.to_datetime(df['change_date']).dt.date
        daily_changes = df.groupby(['date', 'change_type']).size().unstack(fill_value=0)
        
        fig1 = go.Figure()
        if 'joined' in daily_changes.columns:
            fig1.add_trace(go.Scatter(x=daily_changes.index, y=daily_changes['joined'], 
                                    mode='lines+markers', name='Подписались', line=dict(color='green')))
        if 'left' in daily_changes.columns:
            fig1.add_trace(go.Scatter(x=daily_changes.index, y=daily_changes['left'], 
                                    mode='lines+markers', name='Отписались', line=dict(color='red')))
        
        fig1.update_layout(title='Динамика подписок и отписок по дням',
                          xaxis_title='Дата', yaxis_title='Количество')
        st.plotly_chart(fig1)
        
        # Круговая диаграмма общего соотношения
        total_joined = len(df[df['change_type'] == 'joined'])
        total_left = len(df[df['change_type'] == 'left'])
        
        fig2 = go.Figure(data=[go.Pie(labels=['Подписались', 'Отписались'], 
                                     values=[total_joined, total_left],
                                     colors=['green', 'red'])])
        fig2.update_layout(title='Общее соотношение подписок и отписок')
        st.plotly_chart(fig2)
        
        # Таблица с детальной информацией
        st.subheader("Детальная информация об изменениях")
        st.dataframe(df)
    
    async def close(self):
        """Закрытие соединения"""
        if self.client:
            await self.client.disconnect()

def main():
    st.set_page_config(page_title="Telegram Channel Statistics", layout="wide")
    st.title("📊 Статистика Telegram канала")
    
    # Инициализация коллектора
    collector = TelegramStatsCollector()
    
    # Боковая панель для настроек
    st.sidebar.header("Настройки")
    
    # Проверка наличия переменных окружения
    if not all([os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'), os.getenv('TELEGRAM_PHONE')]):
        st.sidebar.error("⚠️ Необходимо настроить переменные окружения в файле .env")
        st.sidebar.markdown("""
        Создайте файл `.env` со следующими переменными:
        ```
        TELEGRAM_API_ID=ваш_api_id
        TELEGRAM_API_HASH=ваш_api_hash
        TELEGRAM_PHONE=ваш_номер_телефона
        ```
        """)
        return
    
    # Ввод данных канала
    channel_username = st.sidebar.text_input("Username канала (без @)", placeholder="example_channel")
    
    # Выбор периода
    st.sidebar.subheader("Период анализа")
    start_date = st.sidebar.date_input("Начальная дата", value=datetime.now() - timedelta(days=30))
    end_date = st.sidebar.date_input("Конечная дата", value=datetime.now())
    
    # Кнопки действий
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔍 Собрать данные"):
            if channel_username:
                with st.spinner("Сбор данных..."):
                    asyncio.run(collector.collect_members(channel_username))
            else:
                st.error("Введите username канала")
    
    with col2:
        if st.button("📈 Показать статистику"):
            if channel_username:
                collector.create_visualizations(channel_username, start_date, end_date)
            else:
                st.error("Введите username канала")
    
    # Основная область
    if channel_username:
        st.header(f"Статистика канала: @{channel_username}")
        
        # Текущая статистика
        stats = collector.get_current_stats(channel_username)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего участников", stats['total_members'])
        
        with col2:
            st.metric("Новых за 30 дней", stats['new_members_30d'])
        
        with col3:
            st.metric("Отписались за 30 дней", stats['left_members_30d'])
        
        with col4:
            st.metric("Чистый прирост", stats['net_growth_30d'])
        
        # Визуализации
        if st.button("Обновить графики"):
            collector.create_visualizations(channel_username, start_date, end_date)

if __name__ == "__main__":
    main() 