# DayCraft Pro 🚀 - Optimized for Fast Deployment

## Professional Productivity Tracker

**Deploy-ready Streamlit app with AI scheduling & analytics**

**✅ Deployment now <60s on Streamlit Cloud!**

### ✨ Features
- AI-optimized daily scheduling
- Plotly charts & trends
- Multi-period goals & analytics
- CSV export, history, responsive UI
- Docker + Cloud ready

### 🚀 Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 🐳 Docker
```bash
docker build -t daycraft .
docker run -p 8501:8501 daycraft
```

### ☁️ **Streamlit Cloud Deploy (FREE - Recommended)**

1. Push to **GitHub**
2. **share.streamlit.io** → New app → GitHub repo → Select `app.py` → Deploy

**SQLite Note**: Uses demo mode (in-memory DB). Data resets per session. For persistent DB:
```
# Add to requirements.txt: sqlite-vss, or use cloud DB
# .streamlit/secrets.toml:
db_path = "/tmp/daycraft.db"
```

**Live in 60 seconds!** https://share.streamlit.io/

### ☁️ **Render.com Deploy (Persistent DB)**

1. Push to GitHub
2. **render.com** → New → Web Service → GitHub repo
3. **Settings**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
4. **Env Vars**:
   ```
   PYTHON_VERSION=3.11
   ```

✅ Persistent SQLite with WAL mode works!

### 🐳 Docker (Local/Cloud)
```bash
docker build -t daycraft .
docker run -p 8501:8501 daycraft
```


### 🔧 Render Environment Variables Setup
```
1. Login render.com → Your Service → Environment tab
2. Add Variable:
   Key: PYTHON_VERSION
   Value: 3.11
3. Save → Manual Deploy → Live!
```

### 📱 Heroku Alternative
```
Procfile:
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### 📊 Expected Dashboard
- AI Task Schedule (Morning/Afternoon/Evening)
- Live productivity charts
- Multi-period targets
- Professional metrics & export

**Zero config • Team-ready • Production-grade**

