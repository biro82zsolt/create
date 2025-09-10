# Sportmotivációs kérdőív – Flask app

## Fő funkciók
- **Név mező** a kérdőív elején (kötelező), opcionális azonosító mező.
- **Excel naplózás**: `data/responses.xlsx` – időpont, token, név, azonosító, kérdésenkénti válaszok, összeg/átlag.
- **PDF generálás**: szép egyoldalas összefoglaló a `out/reports` mappába (ReportLab).

## Testreszabás
- A kérdéseket a `data/questions_hu.csv` fájlban tudod szerkeszteni. Csak az `id,text` oszlopok kellenek (Likert 1–5).
- A sablonok a `templates/quiz.html` és `templates/result.html` fájlok.

## Telepítés cPanelen
1. **Python Webalkalmazás** létrehozása (pl. Python 3.10), projekt gyökér: a feltöltött mappa.
2. `pip install -r requirements.txt` a cPanel UI-ban.
3. WSGI: `passenger_wsgi.py` (lásd alább).
4. Alkalmazás URL: pl. `/sportmotivacios-kerdoiv`.
5. **Restart** minden módosítás után.

### `passenger_wsgi.py` minta
```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app as application
```

## Fejlesztői futtatás
```bash
export FLASK_APP=app.py
flask run
# vagy: python app.py
```

