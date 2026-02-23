# LifePause - PythonAnywhere Ready

PythonAnywhere'da ishlashi uchun optimallashtirilgan Flask versiya.

## Yangi funksiyalar
- Auth: signup/login/logout
- Today dashboard: KPI kartalar, pomodoro timer, adaptive break hint
- Daily check-in (energy/stress/mood/sleep)
- Task journal + status update
- Plans: Kanban board (backlog/today/done/blocked)
- Time tracking: manual/timer sessions, weekly totals, top tags
- Insights: Chart.js grafiklar (work vs stress, energy score)
- Settings: profile + break rule konfiguratsiyasi
- CSV export

## Local run
```powershell
cd c:\Users\Omen\Desktop\ezozaxon\pythonanywhere_app
.\start_local.bat
```
Open: `http://127.0.0.1:5000`

## PythonAnywhere deploy
1. PythonAnywhere -> Web -> **Add a new web app** -> **Manual configuration (Flask)**.
2. Bash console:
```bash
cd ~
git clone <repo_url> lifepause
cd ~/lifepause/pythonanywhere_app
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. WSGI faylini quyidagicha qiling:
```python
import sys
path = '/home/<username>/lifepause/pythonanywhere_app'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
4. Web tabda:
- Virtualenv: `/home/<username>/lifepause/pythonanywhere_app/venv`
- Working directory: `/home/<username>/lifepause/pythonanywhere_app`
5. `Reload` qiling.

## Muhim
- DB: `pythonanywhere_app/lifepause_pa.db`
- `SECRET_KEY` ni PythonAnywhere environment variable bilan almashtiring.
- Kod eski DB bilan ishlashi uchun `time_session.source` column auto-create qilinadi.
