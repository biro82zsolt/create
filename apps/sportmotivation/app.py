# -*- coding: utf-8 -*-
import os
import uuid
import json
import time, random
from datetime import datetime
from io import BytesIO

import pandas as pd

# matplotlib headless
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename  # ÚJ: biztonságos fájlnév
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from flask import current_app

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

if DEBUG:
    print("DBG SPORTMOTIVATION_GOOGLE_SHEET_ID:", os.getenv("SPORTMOTIVATION_GOOGLE_SHEET_ID"))
    print("DBG GOOGLE_SA_JSON set?:", bool(os.getenv("GOOGLE_SA_JSON")))
    print("DBG GSHEETS_SA_FILE:", os.getenv("GSHEETS_SA_FILE"))

# --- Flask App ---
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ha valahol enumerate maradt a sablonban, ne hibázzon:
app.jinja_env.globals['enumerate'] = enumerate

# --- Gyökér → /hu ---
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("quiz", lang="hu"))

# --- Healthcheck (deploy környezetben hasznos) ---
@app.route("/healthz")
def healthz():
    return "ok", 200

# --- Font kezelés ---
FONT_PATH = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
    DEFAULT_FONT = 'DejaVuSans'
else:
    if DEBUG: print("⚠ DejaVuSans.ttf nem található, fallback Helvetica!")
    DEFAULT_FONT = 'Helvetica'

# --- Nyelvi beállítások ---
LANG_CONFIG = {
    "hu": {
        "data_file": os.path.join(BASE_DIR, "data/hu/kenyszervalasztas_minta.xlsx"),  # ABS
        "desc_file": os.path.join(BASE_DIR, "data/hu/skala_leiras.txt"),              # ABS
        "title": "Sportmotivációs kérdőív",
        "instruction": "Miért sportolsz? A következő állításpárok közül válaszd ki azt, amelyik jellemzőbb Rád!",
        "name_label": "Név",
        "submit_label": "Küldés",
        "result_prefix": "Eredmény",
        "footer_text": "Készítette: Bíró Zsolt sportpszichológus",
        "scales": ["Belső_tudás","Belső_tökéletesség","Belső_öröm","Introjektált","Külső","Amotiváció"]
    },
    "en": {
        "data_file": os.path.join(BASE_DIR, "data/en/pairs_en.xlsx"),                  # ABS
        "desc_file": os.path.join(BASE_DIR, "data/en/scale_description.txt"),          # ABS
        "title": "Sports Motivation Questionnaire",
        "instruction": "Why do you do sports? Choose the statement that fits you better!",
        "name_label": "Name",
        "submit_label": "Submit",
        "result_prefix": "Result",
        "footer_text": "Created by: Zsolt Bíró, sports psychologist",
        "scales": ["Intrinsic_Knowledge","Intrinsic_Perfection","Intrinsic_Enjoyment","Introjected","Extrinsic","Amotivation"]
    }
}

# --- Automatikus értékelés (HU/EN) ---
def generate_detailed_interpretation(lang, percentages):
    interpretation = []
    if lang == "hu":
        texts = {
            "Belső_tudás": "a sportban való tanulás és felfedezés motivál.",
            "Belső_tökéletesség": "a fejlődés és teljesítmény elérése hajt.",
            "Belső_öröm": "a sport elsősorban örömforrás és élmény.",
            "Introjektált": "a belsővé tett külső elvárások hatnak Rád.",
            "Külső": "a külső elismerés és jutalom fontos számodra.",
            "Amotiváció": "előfordulhat, hogy alacsony a sport iránti belső elköteleződésed."
        }
    else:
        texts = {
            "Intrinsic_Knowledge": "motivated by learning and discovery in sports.",
            "Intrinsic_Perfection": "driven by growth and achievement.",
            "Intrinsic_Enjoyment": "sports is primarily a source of joy and experience.",
            "Introjected": "influenced by internalized external expectations.",
            "Extrinsic": "external recognition and rewards are important.",
            "Amotivation": "low internal commitment to sports might occur."
        }

    for scale, perc in percentages.items():
        level = ("erősen jellemző" if lang=="hu" else "strongly characteristic") if perc >= 25 else \
                ("mérsékelten jellemző" if lang=="hu" else "moderately characteristic") if perc >= 10 else \
                ("kevésbé jellemző" if lang=="hu" else "less characteristic")
        interpretation.append(f"- {scale}: {level}, {texts.get(scale, '')}")

    if percentages.get("Amotiváció", 0) > 0 or percentages.get("Amotivation", 0) > 0:
        interpretation.append("⚠ Amotivációs tendenciák is jellemzőek." if lang=="hu" else "⚠ Amotivation tendencies are present.")
    return interpretation

def _open_sheet(gc):
    sheet_id = os.getenv("SPORTMOTIVATION_GOOGLE_SHEET_ID", "").strip()
    sheet_url = os.getenv("SPORTMOTIVATION_GOOGLE_SHEET_URL", "").strip()
    if sheet_id:
        try:
            return gc.open_by_key(sheet_id)
        except Exception as e:
            if DEBUG: print("open_by_key failed:", type(e).__name__, e)
    if sheet_url:
        try:
            return gc.open_by_url(sheet_url)
        except Exception as e:
            if DEBUG: print("open_by_url failed:", type(e).__name__, e)
    raise RuntimeError("Nem sikerült megnyitni a táblát. Ellenőrizd az ID/URL-t és a megosztást.")

# --- Adatbetöltés ---
def load_data(lang):
    cfg = LANG_CONFIG[lang]
    # Excel olvasás: openpyxl engine (xlrd nélkül is megy .xlsx-re)
    df_pairs = pd.read_excel(cfg["data_file"], engine="openpyxl")
    pairs = df_pairs.iloc[:, :2].dropna(how="all").reset_index(drop=True)
    scales = df_pairs.iloc[:, 2:4].ffill().reset_index(drop=True)
    with open(cfg["desc_file"], "r", encoding="utf-8") as f:
        paragraphs = [p.strip() for p in f.read().split("\n\n") if p.strip()]
    return pairs, scales, paragraphs

# --- PDF Footer ---
def footer(canvas, doc, footer_text):
    canvas.saveState()
    canvas.setFont(DEFAULT_FONT, 8)
    canvas.drawCentredString(A4[0]/2, 15, footer_text)
    canvas.restoreState()

# --- PDF Generátor ---
def generate_pdf(lang, cfg, user_name, paragraphs, score_sums, percentages, pie_fs, bar_fs):
    pdf_buffer = BytesIO()
    doc = BaseDocTemplate(pdf_buffer, pagesize=A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height-2*cm, id='normal')
    template = PageTemplate(id='main', frames=frame, onPage=lambda c, d: footer(c, d, cfg["footer_text"]))
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=DEFAULT_FONT, fontSize=10, leading=14, alignment=TA_JUSTIFY)
    title_style  = ParagraphStyle('Title',  parent=styles['Title'],  fontName=DEFAULT_FONT, fontSize=16, leading=20, alignment=1, textColor=colors.HexColor("#003366"))

    story = []
    logo_path = os.path.join(BASE_DIR, "static", "logo.png")
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm))
        story.append(Spacer(1,0.5*cm))

    story.append(Paragraph(cfg["title"], title_style))
    story.append(Spacer(1,0.5*cm))

    for p in paragraphs:
        story.append(Paragraph(p, normal_style))
        story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"<b>{cfg['result_prefix']} - {user_name}</b>", normal_style))
    for k,v in score_sums.items():
        story.append(Paragraph(f"{k}: {v} ({percentages[k]:.1f}%)", normal_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>Automatikus értelmezés:</b>" if lang == "hu" else "<b>Automatic Interpretation:</b>", normal_style))
    for line in generate_detailed_interpretation(lang, percentages):
        story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 1*cm))
    story.append(Image(pie_fs, width=12*cm, height=12*cm))   # ABS útvonal
    story.append(Spacer(1,0.5*cm))
    story.append(Image(bar_fs, width=14*cm, height=8*cm))    # ABS útvonal

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

# --- Google Sheets kliens + append ---
SHEET_TAB = os.getenv("GSHEETS_SHEET_TAB", "").strip()

def _get_gs_client():
    sa_json = os.getenv("GSHEETS_SA_JSON")
    sa_file = os.getenv("GSHEETS_SA_FILE")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        if sa_json:
            if DEBUG: print("GS AUTH via JSON string")
            info = json.loads(sa_json)
            creds = Credentials.from_service_account_info(info, scopes=scopes)
        elif sa_file:
            if DEBUG: print("GS AUTH via FILE:", sa_file)
            if not os.path.exists(sa_file):
                if DEBUG: print("GSHEETS: SA file NOT FOUND:", sa_file)
                return None
            creds = Credentials.from_service_account_file(sa_file, scopes=scopes)
        else:
            if DEBUG: print("GSHEETS: No SA_JSON and no SA_FILE set")
            return None
        return gspread.authorize(creds)
    except Exception as e:
        if DEBUG: print("GSHEETS AUTH ERROR:", e)
        return None

def _append_with_retry(ws, row):
    delay = 0.5
    for _ in range(5):
        try:
            return ws.append_row(row, value_input_option="USER_ENTERED")
        except Exception as e:
            msg = str(e).lower()
            if any(tok in msg for tok in ["429", "quota", "rate", "503", "500", "timed out"]):
                time.sleep(delay + random.random() * 0.2)
                delay = min(delay * 2, 8)
                continue
            raise

def append_to_gsheet(row_dict: dict):
    """
    Dinamikus fejléc-kezelés:
    - ha nincs semmi, fejlécet hoz létre (row_dict kulcsai)
    - ha már van fejléc, de hiányoznak oszlopok, bővíti az 1. sort
    - majd a konszolidált fejléc sorrendben írja az új sort
    """
    sheet_id = os.getenv("SPORTMOTIVATION_GOOGLE_SHEET_ID", "").strip()
    sheet_url = os.getenv("SPORTMOTIVATION_GOOGLE_SHEET_URL", "").strip()

    if not sheet_id and not sheet_url:
        if DEBUG: print("[GSHEETS] Nincs GSHEETS_SHEET_ID vagy GSHEETS_SHEET_URL beállítva.")
        return

    gc = _get_gs_client()
    if gc is None:
        if DEBUG: print("[GSHEETS] Auth sikertelen (GSHEETS_SA_JSON / GSHEETS_SA_FILE?)")
        return

    try:
        sh = _open_sheet(gc)
        ws = sh.worksheet(SHEET_TAB) if SHEET_TAB else sh.sheet1

        values = ws.get_all_values()
        desired_headers = list(row_dict.keys())

        if not values:
            # teljesen üres lap → létrehozzuk a fejlécet
            _append_with_retry(ws, desired_headers)
            headers = desired_headers
        else:
            first_row = values[0]
            # van-e valódi fejléc? egyszerű heurisztika: tartalmaz-e tipikus mezőt
            first_lower = [c.strip().lower() for c in first_row]
            header_looks_ok = any(x in first_lower for x in ["timestamp", "lang", "name", "nev", "token"])

            if not header_looks_ok:
                # az első sor nem fejléc, hanem adat → szúrjunk be fejlécet legfelül
                ws.insert_row(desired_headers, 1, value_input_option="USER_ENTERED")
                headers = desired_headers
            else:
                # van fejléc → egészítsük ki az esetleg hiányzó oszlopokkal
                missing = [k for k in desired_headers if k not in first_row]
                if missing:
                    headers = first_row + missing
                    # írd vissza az 1. sort kibővítve
                    ws.update('A1', [headers])
                else:
                    headers = first_row

        # végül írjuk az új sort az összehangolt fejléc sorrendben
        ordered = [row_dict.get(h, "") for h in headers]
        _append_with_retry(ws, ordered)

    except APIError as e:
        try:
            if DEBUG: print("GSHEETS APPEND APIERROR:", e.response.status_code, e.response.text)
        except Exception:
            if DEBUG: print("GSHEETS APPEND APIERROR:", e)
    except Exception as e:
        if DEBUG: print("GSHEETS APPEND ERROR:", repr(e))

# --- Webes végpont: kérdőív ---
@app.route("/<lang>", methods=["GET", "POST"])
def quiz(lang):
    if lang not in LANG_CONFIG:
        return "Language not supported", 404

    pairs, scales, paragraphs = load_data(lang)
    cfg = LANG_CONFIG[lang]

    if request.method == "POST":
        user_name = request.form.get("name")
        if not user_name:
            return "Név megadása kötelező!" if lang=="hu" else "Name is required!", 400

        # Biztonságos fájlnév a PDF-hez
        safe_user = secure_filename(user_name) or "anon"

        responses = [request.form.get(f"q{i+1}") for i in range(len(pairs))]
        # Fallback: ha az első None, de q0 létezik, akkor 0-tól olvasunk
        if responses and responses[0] is None and request.form.get("q0") is not None:
            responses = [request.form.get(f"q{i}") for i in range(len(pairs))]
        score_sums = {k: 0 for k in cfg["scales"]}

        unanswered = [i + 1 for i, r in enumerate(responses) if r not in ("1", "2")]
        if unanswered:
            return ("Kérlek válaszolj minden kérdésre. Hiányzik: "
                    + ", ".join(map(str, unanswered))), 400

        # Skálák pontozása
        for idx, resp in enumerate(responses):
            if resp in ["1","2"]:
                scale = scales.iloc[idx, int(resp)-1]
                for key in score_sums:
                    if str(scale).strip().lower().startswith(key.lower()):
                        score_sums[key] += 1
                        break

        total = sum(score_sums.values())
        percentages = {k: (v/total*100 if total>0 else 0) for k,v in score_sums.items()}

        # Fájlnevek tokennel + ABS útvonalak
        token = uuid.uuid4().hex[:8]
        static_root = current_app.static_folder  # pl. apps/sportmotivation/static
        charts_dir = os.path.join(static_root, "charts")
        results_dir = os.path.join(static_root, "results")
        os.makedirs(charts_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

        pie_fs = os.path.join(charts_dir, f"pie_{lang}_{token}.png")
        bar_fs = os.path.join(charts_dir, f"bar_{lang}_{token}.png")
        # Diagramok
        if total > 0:
            plt.figure(figsize=(6, 6))
            plt.pie(list(score_sums.values()), labels=list(score_sums.keys()),
                    autopct='%1.1f%%', startangle=90)
            plt.title(f"{cfg['title']} - {user_name}")
            plt.savefig(pie_fs, dpi=150)
            plt.close()
        else:
            # Ha nincs egyetlen válasz sem, ne dőljön el a pie chart
            plt.figure(figsize=(6, 6))
            plt.text(0.5, 0.5, "Nincs értékelhető adat", ha="center", va="center", fontsize=12)
            plt.axis('off')
            plt.savefig(pie_fs, dpi=150)
            plt.close()

        plt.figure(figsize=(6,6))
        plt.pie(score_sums.values(), labels=score_sums.keys(), autopct='%1.1f%%', startangle=90)
        plt.title(f"{cfg['title']} - {user_name}")
        plt.savefig(pie_fs, dpi=150)
        plt.close()

        plt.figure(figsize=(7,5))
        plt.barh(list(score_sums.keys()), list(percentages.values()), color="#003366")
        plt.xlabel("%")
        plt.tight_layout()
        plt.savefig(bar_fs, dpi=150)
        plt.close()

        # PDF
        pdf_buffer = generate_pdf(lang, cfg, user_name, paragraphs, score_sums, percentages, pie_fs, bar_fs)

        # PDF mentés
        pdf_filename = f"{cfg['result_prefix']}_{safe_user}_{token}.pdf"
        pdf_path = os.path.join(results_dir, pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.getvalue())

        # Google Sheets naplózás
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "token": token,
            "lang": lang,
            ("nev" if lang=="hu" else "name"): user_name
        }
        for i, r in enumerate(responses):
            row[f"q{i+1}"] = r
        for k,v in score_sums.items():
            row[f"score_{k}"] = v
            row[f"perc_{k}"] = round(percentages[k], 2)

        try:
            append_to_gsheet(row.copy())
        except Exception as e:
            if DEBUG: print("GSheets logging skipped:", e)

        pdf_url = url_for('static', filename=f"results/{pdf_filename}")
        return render_template(
            "result.html",
            lang=lang,
            cfg=cfg,
            user_name=user_name,
            score_sums=score_sums,
            percentages=percentages,
            pdf_url=pdf_url,
            token=token,
            now=datetime.now(),
            **cfg
        )

    # GET
    return render_template(
        "quiz.html",
        lang=lang,
        cfg=cfg,
        pairs=pairs.values.tolist(),
        now=datetime.now(),
        **cfg
    )

if __name__ == "__main__":
    # Deploy: debug=False
    app.run(debug=False)
