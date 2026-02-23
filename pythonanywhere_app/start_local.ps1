Set-Location $PSScriptRoot

if (!(Test-Path '.venv\Scripts\python.exe')) {
  python -m venv .venv
}

.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
