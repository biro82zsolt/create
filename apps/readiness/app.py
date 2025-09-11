from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
import os
import gspread
from google.oauth2.service_account import Credentials
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
# ---- Google Sheets client init ----
GOOGLE_SA_PATH = os.environ.get(
    "GOOGLE_SA_PATH",
    os.path.join(os.path.dirname(__file__), "creds", "readiness-web-sa.json")
)
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")  # <- az ID az URL-ből

_scopes = ["https://www.googleapis.com/auth/spreadsheets"]
_gs_client = None
_ws = None

def pdf_link_callback(uri, rel):
    # Engedjük, hogy a PDF generator a /static/... URL-eket fájlúttá fordítsa
    if uri.startswith("http"):
        return uri
    if uri.startswith("/static/"):
        path = os.path.join(app.root_path, uri.lstrip("/"))
        return path
    # egyéb relatív utak
    return os.path.join(app.root_path, uri)

def _get_creds():
    """
    1) Ha van GOOGLE_SA_JSON (vagy GSHEETS_SA_JSON) az env-ben, azt használjuk.
    2) Különben GOOGLE_SA_PATH (vagy GSHEETS_SA_PATH) fájlból olvasunk.
    """
    sa_json = os.environ.get("GOOGLE_SA_JSON") or os.environ.get("GSHEETS_SA_JSON")
    if sa_json:
        try:
            info = json.loads(sa_json)
        except json.JSONDecodeError:
            info = json.loads(sa_json.strip().strip("'").strip('"'))
        return Credentials.from_service_account_info(info, scopes=_scopes)

    sa_path = os.environ.get("GOOGLE_SA_PATH") or os.environ.get("GSHEETS_SA_PATH")
    if not sa_path:
        # fallback a projekt /creds/readiness-web-sa.json fájlra
        sa_path = os.path.join(os.path.dirname(__file__), "creds", "readiness-web-sa.json")
    if not os.path.exists(sa_path):
        raise FileNotFoundError(f"Service Account JSON not found at: {sa_path}")
    return Credentials.from_service_account_file(sa_path, scopes=_scopes)

def _init_gsheet():
    global _gs_client, _ws
    if _gs_client is not None and _ws is not None:
        return

    sheet_id = os.environ.get("READINESS_GOOGLE_SHEET_ID") or os.environ.get("READINESS_GSHEETS_SHEET_ID")
    if not sheet_id:
        raise RuntimeError("Missing GOOGLE_SHEET_ID / GSHEETS_SHEET_ID env var")

    creds = _get_creds()
    _gs_client = gspread.authorize(creds)

    sh = _gs_client.open_by_key(sheet_id)

    tab = os.environ.get("GOOGLE_SHEET_TAB") or os.environ.get("GSHEETS_SHEET_TAB")
    if tab:
        try:
            _ws = sh.worksheet(tab)
        except gspread.WorksheetNotFound:
            _ws = sh.sheet1
    else:
        _ws = sh.sheet1

def _ensure_headers():
    _init_gsheet()
    headers = _ws.row_values(1)
    desired = [
        "timestamp","lang","name","age_group","sport",
        "iprrs1","iprrs2","iprrs3","iprrs4","iprrs5","iprrs6",
        "iprrs_total","readiness_category",
        "afaq1","afaq2","afaq3","afaq4","afaq5","afaq6","afaq7","afaq8","afaq9","afaq10",
        "afaq_total","afaq_level",
        "iprrs_min_items","iprrs_max_items","afaq_min_items","afaq_max_items"
    ]
    if headers != desired:
        if headers:
            _ws.delete_rows(1)
        _ws.insert_row(desired, 1)

def _join_items_for_sheet(pairs):
    # pairs: [(idx, text, score), ...]
    # egy sorban: "1. Szöveg (3) | 6. Szöveg (3)"
    return " | ".join([f"{i}. {t} ({s})" for i,t,s in pairs])

def append_submission_to_sheet(data):
    _ensure_headers()
    row = [
        data["timestamp"], data["lang"], data.get("name",""), data.get("age_group",""), data.get("sport",""),
        *data["iprrs_scores"], data["iprrs_total"], data["readiness_category"],
        *data["afaq_scores"], data["afaq_total"], data["afaq_level"],
        _join_items_for_sheet(data["iprrs_mins"]),
        _join_items_for_sheet(data["iprrs_maxs"]),
        _join_items_for_sheet(data["afaq_mins"]),
        _join_items_for_sheet(data["afaq_maxs"]),
    ]
    print("Appending row to Google Sheet:", row)
    _ws.append_row(row, value_input_option="RAW")

@app.context_processor
def _lang_switcher():
    def switch_lang(to_lang: str):
        args = request.args.to_dict(flat=True)
        args["lang"] = to_lang
        endpoint = request.endpoint or "quiz"  # vagy a te fő végpontod
        values = (request.view_args or {}).copy()
        return url_for(endpoint, **values, **args)
    return dict(switch_lang_url=switch_lang_url)

# -----------------------------
# Texts (EN/HU)
# -----------------------------
TEXTS = {
    "en": {
        "title": "Sport Psychological Readiness – I-PRRS & AFAQ",
        "iprrs_title": "Injury–Psychological Readiness to Return to Sport (I-PRRS)",
        "iprrs_intro": "Please rate your confidence to return your sport on a scale from 0 to 10 (0 = no confidence at all; 5 = moderate confidence; 10 = complete confidence).",
        "iprrs_items": [
            "My overall confidence to play is",
            "My confidence to play without pain is",
            "My confidence to give 100% effort is",
            "My confidence in injured body part to handle the demands of the situation is",
            "My confidence in skill level/ability is",
            "My confidence to not concentrate on the injury is",
        ],
        "iprrs_note": "Psychological Readiness: fully confident to return to play is defined here as having a > 50 score on the I-PRRS.",
        "afaq_title": "Athlete Fear Avoidance Questionnaire (AFAQ)",
        "afaq_intro": "Indicate the degree to which you have these thoughts and feelings when you are in pain due to a sports injury.",
        "afaq_scale": [
            "Not at all", "To a slight degree", "To a moderate degree", "To a great degree", "Completely agree"
        ],
        "afaq_items": [
            "I will never be able to play as I did before my injury",
            "I am worried about my role with the team changing",
            "I am worried about what other people will think of me if I don't perform at the same level.",
            "I am not sure what my injury is",
            "I believe that my current injury has jeopardized my future athletic abilities",
            "I am not comfortable going back to play until I am 100%",
            "People don't understand how serious my injury is",
            "I don't know if I am ready to play",
            "I worry if I go back to play too soon I will make my injury worse",
            "When my pain is intense, I worry that my injury is a very serious one",
        ],
        "labels": {
            "language": "Language",
            "english": "English",
            "hungarian": "Hungarian",
            "submit": "View result",
            "download_pdf": "Download PDF",
            "back": "Back",
            "iprrs_total": "I-PRRS total",
            "iprrs_ready": "I-PRRS readiness",
            "ready": "Ready to return (>50)",
            "not_ready": "Caution: below threshold (≤50)",
            "afaq_total": "AFAQ total",
            "afaq_level": "AFAQ level (higher = more fear-avoidance)",
            "afaq_levels": {"low": "Low level of fear is typical", "moderate": "Moderate level of fear is typical", "high": "High level of fear is typical"},
            "footnote": "This tool is informational and not a medical diagnosis.",
            "name": "Name",
            "age_group": "Age group",
            "sport": "Sport",
            "participant": "Participant",
            "readiness_category": "Readiness category",
            "fa_category": "Fear avoidance category",
            "min_items": "Lowest-scoring items",
            "max_items": "Highest-scoring items",
            "iprrs": "I-PRRS",
            "afaq": "AFAQ",
            "ready_code": {"ready": "Ready for returning to play", "not_ready": "Not ready for returning to play"},
        },
    },
    "hu": {
        "title": "Sport mentális felkészültség – I-PRRS és AFAQ",
        "iprrs_title": "Sérülés utáni pszichológiai készenlét a sportba való visszatérésre (I-PRRS)",
        "iprrs_intro": "Értékeld a sportba való visszatérésben érzett magabiztosságod 0–10 skálán (0 = egyáltalán nem; 5 = közepes; 10 = teljes).",
        "iprrs_items": [
            "Összességében mennyire vagy magabiztos a játékban?",
            "Mennyire vagy magabiztos abban, hogy fájdalom nélkül tudsz játszani?",
            "Mennyire vagy magabiztos abban, hogy 100% erőbedobással tudsz játszani?",
            "Mennyire bízol benne, hogy a sérült testrészed bírja a terhelést?",
            "Mennyire bízol a készségeidben/képességedben?",
            "Mennyire vagy magabiztos abban, hogy nem a sérülésre koncentrálsz?",
        ],
        "iprrs_note": "Pszichológiai készenlét: a teljes visszatérésre való készség – jelenleg > 50 I-PRRS pontként jelezzük.",
        "afaq_title": "Sportolói félelmi elkerülés kérdőív (AFAQ)",
        "afaq_intro": "Jelöld meg, milyen mértékben jellemzőek rád ezek a gondolatok/érzések, amikor sportsérülés miatti fájdalmat érzel.",
        "afaq_scale": [
            "Egyáltalán nem", "Kis mértékben", "Közepes mértékben", "Nagy mértékben", "Teljesen egyetértek"
        ],
        "afaq_items": [
            "Soha nem fogok úgy játszani, mint a sérülésem előtt",
            "Aggódom, hogy megváltozik a szerepem a csapatban",
            "Aggódom, hogy mások mit gondolnak rólam, ha nem ugyanazon a szinten teljesítek",
            "Nem vagyok biztos benne, pontosan mi a sérülésem",
            "Úgy gondolom, a jelenlegi sérülésem veszélyeztette a jövőbeli sportképességeimet",
            "Nem érzem kényelmesnek a visszatérést, amíg nem vagyok 100%-os",
            "Az emberek nem értik, mennyire komoly a sérülésem",
            "Nem tudom, készen állok-e a játékra",
            "Aggódom, ha túl hamar térek vissza, rosszabb lesz a sérülésem",
            "Amikor erős a fájdalmam, attól tartok, hogy a sérülésem nagyon komoly",
        ],
        "labels": {
            "language": "Nyelv",
            "english": "Angol",
            "hungarian": "Magyar",
            "submit": "Eredmény megtekintése",
            "download_pdf": "PDF letöltése",
            "back": "Vissza",
            "iprrs_total": "I-PRRS összpontszám",
            "iprrs_ready": "I-PRRS készenlét",
            "ready": "Visszatérésre kész (>50)",
            "not_ready": "Óvatosság: küszöb alatt (≤50)",
            "afaq_total": "AFAQ összpontszám",
            "afaq_level": "AFAQ szint (magasabb = erősebb elkerülés)",
            "afaq_levels": {"low": "Alacsony szintű félelem jellemző", "moderate": "Közepes mértékű félelem jellemző", "high": "Magas szintű félelem jellemző"},
            "footnote": "Az eszköz tájékoztató jellegű, nem minősül orvosi diagnózisnak.",
            "name": "Név",
            "age_group": "Korosztály",
            "sport": "Sportág",
            "participant": "Kitöltő",
            "readiness_category": "Readiness kategória",
            "fa_category": "Fear Avoidance kategória",
            "min_items": "Legalacsonyabb tételek",
            "max_items": "Legmagasabb tételek",
            "iprrs": "I-PRRS",
            "afaq": "AFAQ",
            "ready_code": {"ready": "Készen áll a visszatérésre", "not_ready": "Nem áll készen a visszatérésre"},
        },
    },
}

READINESS_THRESHOLD = 50

# -----------------------------
# Helpers
# -----------------------------
def compute_scores(form):
    lang = form.get("lang", "hu")
    name = form.get("name", "").strip()
    age_group = form.get("age_group", "").strip()
    sport = form.get("sport", "").strip()

    iprrs_scores = [int(form.get(f"iprrs{i}", 0)) for i in range(1, 7)]
    iprrs_total = sum(iprrs_scores)
    iprrs_ready = iprrs_total > READINESS_THRESHOLD
    readiness_category = "ready" if iprrs_ready else "not_ready"

    afaq_scores = [int(form.get(f"afaq{i}", 0)) for i in range(1, 11)]
    afaq_total = sum(afaq_scores)
    if afaq_total <= 20:
        afaq_level = "low"
    elif afaq_total <= 35:
        afaq_level = "moderate"
    else:
        afaq_level = "high"

    # Min/Max itemek (aktuális nyelvű szövegekkel)
    iprrs_items = TEXTS[lang]["iprrs_items"]
    afaq_items = TEXTS[lang]["afaq_items"]
    iprrs_mins, iprrs_maxs = _min_max_items(iprrs_scores, iprrs_items)
    afaq_mins, afaq_maxs = _min_max_items(afaq_scores, afaq_items)

    return {
        "lang": lang,
        "name": name,
        "age_group": age_group,
        "sport": sport,
        "iprrs_scores": iprrs_scores,
        "iprrs_total": iprrs_total,
        "iprrs_ready": iprrs_ready,
        "readiness_category": readiness_category,
        "afaq_scores": afaq_scores,
        "afaq_total": afaq_total,
        "afaq_level": afaq_level,
        "iprrs_mins": iprrs_mins,
        "iprrs_maxs": iprrs_maxs,
        "afaq_mins": afaq_mins,
        "afaq_maxs": afaq_maxs,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _min_max_items(scores, items):
    """Többes holtverseny kezelése: visszaadja a min és max értékű tételek listáját [(idx, text, score), ...]."""
    if not scores:
        return [], []
    min_val = min(scores)
    max_val = max(scores)
    mins = [(i+1, items[i], scores[i]) for i in range(len(scores)) if scores[i] == min_val]
    maxs = [(i+1, items[i], scores[i]) for i in range(len(scores)) if scores[i] == max_val]
    return mins, maxs

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    # default language hu
    lang = request.args.get("lang", "hu")
    return render_template("index.html", texts=TEXTS[lang], lang=lang)

@app.route("/submit", methods=["POST"], endpoint="readiness_submit")
def readiness_submit():
    data = compute_scores(request.form)
    session["result"] = data
    try:
        append_submission_to_sheet(data)  # ha használod a Sheets mentést
    except Exception as e:
        print("Sheets append error:", e)
    return redirect(url_for("result"))

@app.route("/result", methods=["GET"])
def result():
    data = session.get("result")
    if not data:
        return redirect(url_for("index"))
    texts = TEXTS[data["lang"]]
    return render_template("result.html", data=data, texts=texts, threshold=READINESS_THRESHOLD)

@app.route("/download-pdf", methods=["GET"])
def download_pdf():
    data = session.get("result")
    if not data:
        return redirect(url_for("index"))
    texts = TEXTS[data["lang"]]
    html = render_template("result_pdf.html", data=data, texts=texts, threshold=READINESS_THRESHOLD)

    # Generate PDF in-memory with xhtml2pdf
    pdf_io = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_io, link_callback=pdf_link_callback)  # type: ignore
    if pisa_status.err:
        return "PDF generation error", 500

    pdf_io.seek(0)
    filename = f"sport-readiness-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"
    return send_file(pdf_io, as_attachment=True, download_name=filename, mimetype="application/pdf")

if __name__ == "__main__":
    # For local dev
    app.run(debug=True)
