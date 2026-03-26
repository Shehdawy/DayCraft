# database.py - Professional DayCraft Database Layer
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pandas as pd

DB_NAME = 'daycraft.db'

def init_db(use_memory: bool = False):
    """
    Production-safe DB initialization with auto cloud detection.
    use_memory=True: :memory: DB for cloud/demo (fast, non-persistent)
    """
    # Auto-detect cloud environments for fastest deploys
    import os
    cloud_env = (
        'STREAMLIT_CLOUD_APP_ID' in os.environ or
        'RENDER' in os.environ.get('ENVIRONMENT', '') or
        os.environ.get('DYNO') == 'run:web'  # Heroku
    )
    
    if cloud_env or use_memory:
        DB_PATH = ':memory:'
    else:
        DB_PATH = DB_NAME
        # WAL mode for local/Render persistent
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    # Production-safe: CREATE IF NOT EXISTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration REAL NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('High','Medium','Low')),
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Completed','Missed')),
            break_day INTEGER DEFAULT 0,
            date TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT UNIQUE CHECK(period IN ('Day','Week','Month','6Months','Year')),
            goal INTEGER DEFAULT 0,
            achieved INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert defaults only if tables empty
    cursor.execute("SELECT COUNT(*) FROM targets")
    if cursor.fetchone()[0] == 0:
        default_targets = [
            ('Day', 5), ('Week', 25), ('Month', 100), ('6Months', 500), ('Year', 1000)
        ]
        cursor.executemany('INSERT INTO targets (period, goal) VALUES (?, ?)', default_targets)
    
    # WAL mode for concurrent access (Streamlit Cloud)
    if not use_memory:
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
    
    conn.commit()
    conn.close()

def add_task(name: str, duration: float, priority: str, break_day: int = 0, date: str = None) -> int:
    """Add task and return ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO tasks (name, duration, priority, break_day, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, duration, priority, break_day, date))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_task_status(task_id: int, status: str):
    """Update task status."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
    conn.commit()
    conn.close()

def get_tasks_for_date(date: str) -> List[Tuple]:
    """Get tasks for specific date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE date = ? ORDER BY priority DESC', (date,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_tasks_period(period: str, days: int = 7) -> pd.DataFrame:
    """Get tasks dataframe for period."""
    conn = sqlite3.connect(DB_NAME)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    df = pd.read_sql_query('''
        SELECT date, status, COUNT(*) as count 
        FROM tasks 
        WHERE date BETWEEN ? AND ? 
        GROUP BY date, status 
        ORDER BY date
    ''', conn, params=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    conn.close()
    return df

def get_all_tasks_history() -> pd.DataFrame:
    """Get complete task history."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('SELECT * FROM tasks ORDER BY date DESC, created_at DESC LIMIT 1000', conn)
    conn.close()
    return df

def get_target(period: str) -> Tuple[int, int]:
    """Get target goal and achieved."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT goal, achieved FROM targets WHERE period = ?', (period,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 0)

def set_target(period: str, goal: int):
    """Set target goal."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO targets (period, goal) 
        VALUES (?, ?)
    ''', (period, goal))
    conn.commit()
    conn.close()

def update_period_achieved(period: str):
    """Update achieved count for period based on completed tasks."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    days_map = {'Day': 1, 'Week': 7, 'Month': 30, '6Months': 180, 'Year': 365}
    days = days_map.get(period, 30)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT COUNT(*) FROM tasks 
        WHERE status = 'Completed' AND date BETWEEN ? AND ?
    ''', (start_date, end_date))
    
    achieved = cursor.fetchone()[0]
    cursor.execute('UPDATE targets SET achieved = ?, updated_at = CURRENT_TIMESTAMP WHERE period = ?', (achieved, period))
    conn.commit()
    conn.close()

def export_to_csv() -> str:
    """Export tasks to CSV file."""
    df = get_all_tasks_history()
    filename = f'daycraft_export_{datetime.now().strftime("%Y%m%d")}.csv'
    df.to_csv(filename, index=False)
    return filename

