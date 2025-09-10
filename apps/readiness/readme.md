# Sport Readiness (I-PRRS & AFAQ)

Flask app két sportpszichológiai kérdőívvel (I-PRRS, AFAQ), eredmény oldallal, PDF exporttal és Google Sheets mentéssel.

## Quick start (dev)

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt

# .env létrehozása az .env.example alapján
# - FLASK_SECRET_KEY
# - GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB
# - GOOGLE_SA_PATH vagy GOOGLE_SA_JSON
# NE feledd: a Sheetet oszd meg Editor joggal a service account client_email címével!

python app.py
# http://127.0.0.1:5000
