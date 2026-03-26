
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from database import (
    init_db, add_task, update_task_status, get_tasks_for_date, 
    get_target, set_target, update_period_achieved, export_to_csv,
    get_all_tasks_history, get_tasks_period
)
# Import scheduler functions only, no heavy calls at import
from scheduler import (
    ai_schedule_day, daily_evaluation, weekly_evaluation, 
    monthly_evaluation, yearly_evaluation, get_productivity_trend
)

# Config
st.set_page_config(
    page_title='DayCraft', 
    page_icon='🚀', 
    layout='wide'
)

# Initialize DB
@st.cache_data
def init_app():
    if 'initialized' not in st.session_state:
        init_db()
        st.session_state.initialized = True
        st.session_state.selected_date = datetime.now().strftime('%Y-%m-%d')

init_app()

# --- Main App ---
st.title("🚀 DayCraft Pro - Productivity Tracker")

# Date selector
st.session_state.selected_date = st.date_input(
    'Select Date', value=datetime.now(), key='date_picker'
).strftime('%Y-%m-%d')

# Sidebar: add task
st.sidebar.markdown('## ➕ Add Task')
with st.sidebar.form('task_form', clear_on_submit=True):
    task_name = st.text_input('Task name', placeholder='e.g., Code review')
    duration = st.number_input('Duration (h)', 0.25, 12.0, 1.0, 0.25)
    priority = st.selectbox('Priority', ['High', 'Medium', 'Low'], index=1)
    date = st.date_input('Date', value=datetime.now())
    break_day = st.checkbox('Rest day')
    submitted = st.form_submit_button('Add Task')
    
    if submitted and task_name:
        task_id = add_task(task_name, duration, priority, break_day, date.strftime('%Y-%m-%d'))
        st.success(f'✅ Task #{task_id} added!')

# Metrics
tasks = get_tasks_for_date(st.session_state.selected_date)
total = len(tasks)
completed = sum(1 for t in tasks if t[4] == 'Completed')
productivity = (completed / max(total, 1)) * 100
col1, col2, col3 = st.columns(3)
col1.metric('📊 Total Tasks', total)
col2.metric('✅ Completed', completed)
col3.metric('🎯 Productivity', f'{productivity:.0f}%')

# --- Scheduler (SAFE) ---
st.markdown('## 📅 AI Daily Schedule')
if st.button("Generate AI Schedule"):
    schedule = ai_schedule_day(st.session_state.selected_date)
    if schedule:
        for block in ['Morning','Afternoon','Evening']:
            st.markdown(f"### {block}")
            for task in schedule.get(block, []):
                st.write(f"{task[1]} • {task[2]}h • {task[3]} • {task[4]}")

# --- Analytics (Safe) ---
st.markdown('## 📈 Analytics & Trends')
if st.button("Show Analytics"):
    trend_df = get_productivity_trend(30)
    if not trend_df.empty:
        fig = px.line(trend_df, x='date', y='completed', title='30-Day Productivity Trend')
        st.plotly_chart(fig)

# --- History Export ---
if st.button("Export Task History"):
    filename = export_to_csv()
    st.success(f'Exported to {filename}')