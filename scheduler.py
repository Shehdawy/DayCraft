# scheduler.py - Professional AI Scheduling & Analytics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from database import get_tasks_for_date, get_tasks_period
import pandas as pd

PRIORITY_ORDER = {'High': 1, 'Medium': 2, 'Low': 3}
BLOCK_CAPACITY = {'Morning': 4, 'Afternoon': 6, 'Evening': 4}

def ai_schedule_day(date: str = None) -> Dict[str, List[Tuple]]:
    """AI-optimized daily schedule."""
    tasks = get_tasks_for_date(date) if date else get_tasks_for_date(datetime.now().strftime('%Y-%m-%d'))
    schedule = {block: [] for block in BLOCK_CAPACITY}
    
    # Filter pending tasks - SAFE UNPACKING
    pending_tasks = []
    for task in tasks:
        if len(task) >= 7 and task[4] == 'Pending':
            pending_tasks.append(task)
    
    pending_tasks.sort(key=lambda x: PRIORITY_ORDER.get(x[3], 3))
    
    capacity = BLOCK_CAPACITY.copy()
    
    for task in pending_tasks:
        if len(task) < 7:
            continue
        task_id, name, duration, priority, status, break_day, date = task[:7]
        if break_day:
            continue
            
        for block in ['Morning', 'Afternoon', 'Evening']:
            if duration <= capacity[block]:
                schedule[block].append(task)
                capacity[block] -= duration
                break
    
    return schedule

def productivity_evaluation(period_data: pd.DataFrame) -> str:
    """Comprehensive productivity score."""
    if period_data.empty:
        return 'No data yet 🆕'
    
    total = period_data['count'].sum()
    completed = period_data[period_data['status'] == 'Completed']['count'].sum()
    
    if total == 0:
        return 'No tasks assigned 😌'
    
    rate = completed / total
    if rate >= 0.9:
        return f'🏆 Elite Performer ({completed}/{total}, {rate:.1%})'
    elif rate >= 0.75:
        return f'💪 Excellent ({completed}/{total}, {rate:.1%})'
    elif rate >= 0.5:
        return f'✅ Good ({completed}/{total}, {rate:.1%})'
    else:
        return f'⚠️ Needs Focus ({completed}/{total}, {rate:.1%})'

def daily_evaluation() -> str:
    """Daily productivity evaluation."""
    df = get_tasks_period('trend', 1)
    return productivity_evaluation(df)

def weekly_evaluation() -> str:
    """Weekly productivity with trend."""
    df = get_tasks_period('trend', 7)
    return productivity_evaluation(df)

def monthly_evaluation() -> str:
    """Monthly productivity insights."""
    df = get_tasks_period('trend', 30)
    return productivity_evaluation(df)

def yearly_evaluation() -> str:
    """Yearly achievement overview."""
    df = get_tasks_period('trend', 365)
    return productivity_evaluation(df)

def get_productivity_trend(days: int = 30) -> pd.DataFrame:
    """Get productivity trend data for charts."""
    df = get_tasks_period('trend', days)
    if not df.empty:
        daily_stats = df[df['status'] == 'Completed'].groupby('date')['count'].sum().reset_index()
        daily_stats.columns = ['date', 'completed']
        return daily_stats.fillna(0)
    return pd.DataFrame({'date': [], 'completed': []})

