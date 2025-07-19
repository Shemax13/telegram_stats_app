import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import csv
import os

class DataExporter:
    def __init__(self, db_path='telegram_stats.db'):
        self.db_path = db_path
    
    def export_members_to_csv(self, channel_username: str, filename: str = None):
        """Экспорт участников канала в CSV"""
        if not filename:
            filename = f"members_{channel_username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                username,
                first_name,
                last_name,
                joined_date,
                is_active
            FROM channel_members
            WHERE channel_username = ?
            ORDER BY joined_date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[channel_username])
        conn.close()
        
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Данные экспортированы в {filename}")
        return filename
    
    def export_changes_to_csv(self, channel_username: str, start_date: datetime, end_date: datetime, filename: str = None):
        """Экспорт изменений за период в CSV"""
        if not filename:
            filename = f"changes_{channel_username}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                change_type,
                change_date,
                username,
                first_name,
                last_name
            FROM member_changes
            WHERE channel_username = ? AND change_date BETWEEN ? AND ?
            ORDER BY change_date
        '''
        
        df = pd.read_sql_query(query, conn, params=[channel_username, start_date, end_date])
        conn.close()
        
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Изменения экспортированы в {filename}")
        return filename
    
    def export_stats_to_json(self, channel_username: str, filename: str = None):
        """Экспорт статистики в JSON"""
        if not filename:
            filename = f"stats_{channel_username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        conn = sqlite3.connect(self.db_path)
        
        # Общая статистика
        total_members = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM channel_members WHERE is_active = 1', 
            conn
        ).iloc[0]['count']
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_members_30d = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM channel_members WHERE joined_date >= ? AND is_active = 1',
            conn,
            params=[thirty_days_ago]
        ).iloc[0]['count']
        
        left_members_30d = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM member_changes WHERE change_type = "left" AND change_date >= ?',
            conn,
            params=[thirty_days_ago]
        ).iloc[0]['count']
        
        # Статистика по дням
        daily_stats = pd.read_sql_query('''
            SELECT 
                DATE(change_date) as date,
                change_type,
                COUNT(*) as count
            FROM member_changes
            WHERE change_date >= ?
            GROUP BY DATE(change_date), change_type
            ORDER BY date
        ''', conn, params=[thirty_days_ago])
        
        conn.close()
        
        stats = {
            'channel_username': channel_username,
            'export_date': datetime.now().isoformat(),
            'total_members': total_members,
            'last_30_days': {
                'new_members': new_members_30d,
                'left_members': left_members_30d,
                'net_growth': new_members_30d - left_members_30d
            },
            'daily_stats': daily_stats.to_dict('records')
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"Статистика экспортирована в {filename}")
        return filename
    
    def export_growth_report(self, channel_username: str, days: int = 30, filename: str = None):
        """Экспорт отчета о росте канала"""
        if not filename:
            filename = f"growth_report_{channel_username}_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        conn = sqlite3.connect(self.db_path)
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Ежедневная статистика
        daily_growth = pd.read_sql_query('''
            SELECT 
                DATE(change_date) as date,
                SUM(CASE WHEN change_type = 'joined' THEN 1 ELSE 0 END) as joined,
                SUM(CASE WHEN change_type = 'left' THEN 1 ELSE 0 END) as left,
                SUM(CASE WHEN change_type = 'joined' THEN 1 ELSE -1 END) as net_change
            FROM member_changes
            WHERE change_date >= ?
            GROUP BY DATE(change_date)
            ORDER BY date
        ''', conn, params=[since_date])
        
        conn.close()
        
        # Добавляем кумулятивные значения
        daily_growth['cumulative_joined'] = daily_growth['joined'].cumsum()
        daily_growth['cumulative_left'] = daily_growth['left'].cumsum()
        daily_growth['cumulative_net'] = daily_growth['net_change'].cumsum()
        
        daily_growth.to_csv(filename, index=False, encoding='utf-8')
        print(f"Отчет о росте экспортирован в {filename}")
        return filename
    
    def create_summary_report(self, channel_username: str, filename: str = None):
        """Создание сводного отчета"""
        if not filename:
            filename = f"summary_report_{channel_username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        conn = sqlite3.connect(self.db_path)
        
        # Общая статистика
        total_members = pd.read_sql_query(
            'SELECT COUNT(*) as count FROM channel_members WHERE is_active = 1', 
            conn
        ).iloc[0]['count']
        
        # Статистика за разные периоды
        periods = [7, 30, 90]
        period_stats = {}
        
        for days in periods:
            since_date = datetime.now() - timedelta(days=days)
            new_members = pd.read_sql_query(
                'SELECT COUNT(*) as count FROM channel_members WHERE joined_date >= ? AND is_active = 1',
                conn,
                params=[since_date]
            ).iloc[0]['count']
            
            left_members = pd.read_sql_query(
                'SELECT COUNT(*) as count FROM member_changes WHERE change_type = "left" AND change_date >= ?',
                conn,
                params=[since_date]
            ).iloc[0]['count']
            
            period_stats[days] = {
                'new': new_members,
                'left': left_members,
                'net': new_members - left_members
            }
        
        conn.close()
        
        # Создание отчета
        report = f"""
СВОДНЫЙ ОТЧЕТ ПО КАНАЛУ @{channel_username}
Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ОБЩАЯ СТАТИСТИКА:
- Всего участников: {total_members:,}

СТАТИСТИКА ЗА ПОСЛЕДНИЕ ПЕРИОДЫ:
"""
        
        for days in periods:
            stats = period_stats[days]
            report += f"""
За последние {days} дней:
- Новых участников: {stats['new']:,}
- Отписавшихся: {stats['left']:,}
- Чистый прирост: {stats['net']:,}
"""
        
        report += f"""
РЕКОМЕНДАЦИИ:
- Средний прирост в день: {period_stats[30]['net'] / 30:.1f}
- Коэффициент удержания: {(period_stats[30]['new'] - period_stats[30]['left']) / period_stats[30]['new'] * 100:.1f}%
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Сводный отчет создан: {filename}")
        return filename

def main():
    """Пример использования экспортера"""
    exporter = DataExporter()
    
    # Пример экспорта данных
    channel_username = "example_channel"  # Замените на реальный username
    
    print("Доступные функции экспорта:")
    print("1. export_members_to_csv() - экспорт участников")
    print("2. export_changes_to_csv() - экспорт изменений")
    print("3. export_stats_to_json() - экспорт статистики")
    print("4. export_growth_report() - отчет о росте")
    print("5. create_summary_report() - сводный отчет")
    
    # Примеры использования:
    # exporter.export_members_to_csv(channel_username)
    # exporter.export_stats_to_json(channel_username)
    # exporter.create_summary_report(channel_username)

if __name__ == "__main__":
    main() 