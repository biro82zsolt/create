import io
import json
import math
import os
import sqlite3
from datetime import datetime
from functools import wraps

import pandas as pd
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "sociometry.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_EMAIL = os.environ.get("SOCIOMETRY_ADMIN_EMAIL", "admin@example.com").lower().strip()
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("SOCIOMETRY_ADMIN_PASSWORD", "admin123"))

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

TEXTS = {
    "hu": {
        "app_name": "Szociometria",
        "admin_login": "Admin bejelentkezés",
        "email": "Email",
        "password": "Jelszó",
        "login": "Belépés",
        "logout": "Kijelentkezés",
        "dashboard": "Admin felület",
        "questionnaires": "Kérdéssorok",
        "rosters": "Névsorok",
        "measurements": "Mérések",
        "upload": "Feltöltés",
        "name": "Név",
        "create_measurement": "Új mérés létrehozása",
        "questionnaire": "Kérdéssor",
        "roster": "Névsor",
        "measurement_name": "Mérés neve",
        "user_identifier": "Felhasználói azonosító",
        "user_password": "Felhasználói jelszó",
        "save": "Mentés",
        "sociogram_indices": "Szociogram kérdések indexei (pl. 1,3,5)",
        "go_to_user": "Felhasználói felület",
        "instruction": "Kérlek válaszolj pontosan három csapattársad nevével. Magadat ne válaszd!",
        "your_name": "Saját név",
        "submit": "Beküldés",
        "results": "Eredmények",
        "download_excel": "Excel letöltés",
        "download_pdf": "PDF letöltés",
        "sociogram": "Szociogram",
        "language": "Nyelv",
        "theme": "Téma",
        "dark": "Sötét",
        "light": "Világos",
        "user_login": "Felhasználói bejelentkezés",
        "identifier": "Azonosító",
        "open_measurement": "Kérdőív megnyitása",
    },
    "en": {
        "app_name": "Sociometry",
        "admin_login": "Admin login",
        "email": "Email",
        "password": "Password",
        "login": "Login",
        "logout": "Logout",
        "dashboard": "Admin dashboard",
        "questionnaires": "Question sets",
        "rosters": "Rosters",
        "measurements": "Measurements",
        "upload": "Upload",
        "name": "Name",
        "create_measurement": "Create new measurement",
        "questionnaire": "Question set",
        "roster": "Roster",
        "measurement_name": "Measurement name",
        "user_identifier": "User identifier",
        "user_password": "User password",
        "save": "Save",
        "sociogram_indices": "Sociogram question indices (e.g. 1,3,5)",
        "go_to_user": "User interface",
        "instruction": "Please answer with exactly three teammates. Do not choose yourself!",
        "your_name": "Your name",
        "submit": "Submit",
        "results": "Results",
        "download_excel": "Download Excel",
        "download_pdf": "Download PDF",
        "sociogram": "Sociogram",
        "language": "Language",
        "theme": "Theme",
        "dark": "Dark",
        "light": "Light",
        "user_login": "User login",
        "identifier": "Identifier",
        "open_measurement": "Open questionnaire",
    },
}


def get_lang():
    lang = request.args.get("lang") or session.get("lang") or "hu"
    if lang not in TEXTS:
        lang = "hu"
    session["lang"] = lang
    return lang


def t(key):
    return TEXTS[get_lang()][key]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            questions_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rosters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            names_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            questionnaire_id INTEGER NOT NULL,
            roster_id INTEGER NOT NULL,
            user_identifier TEXT NOT NULL,
            user_password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS measurement_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            include_sociogram INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_id INTEGER NOT NULL,
            respondent_name TEXT NOT NULL,
            answers_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login", lang=get_lang()))
        return func(*args, **kwargs)

    return wrapper


def parse_questionnaire_excel(file_storage):
    df = pd.read_excel(file_storage)
    first_col = df.columns[0]
    questions = [str(v).strip() for v in df[first_col].dropna().tolist() if str(v).strip()]
    if not questions:
        raise ValueError("A kérdéssor fájl üres.")
    return questions


def parse_roster_excel(file_storage):
    df = pd.read_excel(file_storage)
    first_col = df.columns[0]
    names = [str(v).strip() for v in df[first_col].dropna().tolist() if str(v).strip()]
    unique = []
    seen = set()
    for n in names:
        if n.lower() not in seen:
            unique.append(n)
            seen.add(n.lower())
    if len(unique) < 4:
        raise ValueError("Legalább 4 név szükséges.")
    return unique


def load_measurement(measurement_id):
    conn = get_db()
    measurement = conn.execute("SELECT * FROM measurements WHERE id = ?", (measurement_id,)).fetchone()
    if not measurement:
        conn.close()
        return None, None, None, None
    questionnaire = conn.execute("SELECT * FROM questionnaires WHERE id = ?", (measurement["questionnaire_id"],)).fetchone()
    roster = conn.execute("SELECT * FROM rosters WHERE id = ?", (measurement["roster_id"],)).fetchone()
    mq = conn.execute(
        "SELECT question_index, question_text, include_sociogram FROM measurement_questions WHERE measurement_id = ? ORDER BY question_index",
        (measurement_id,),
    ).fetchall()
    conn.close()
    return measurement, questionnaire, roster, mq


def compute_metrics(names, responses, question_index):
    in_degree = {name: 0 for name in names}
    out_degree = {name: 0 for name in names}
    edges = []
    edge_set = set()

    for row in responses:
        sender = row["respondent_name"]
        answers = json.loads(row["answers_json"])
        selected = answers.get(str(question_index), [])
        out_degree[sender] = len(selected)
        for target in selected:
            if target in in_degree:
                in_degree[target] += 1
                edges.append((sender, target))
                edge_set.add((sender, target))

    reciprocal = sum(1 for a, b in edge_set if (b, a) in edge_set and a < b)
    isolates = sum(1 for n in names if in_degree[n] == 0 and out_degree[n] == 0)
    density = len(edge_set) / (len(names) * (len(names) - 1)) if len(names) > 1 else 0
    reciprocity = reciprocal / len(edge_set) if edge_set else 0

    return {
        "in_degree": in_degree,
        "out_degree": out_degree,
        "edges": edges,
        "edge_set": edge_set,
        "reciprocal_pairs": reciprocal,
        "isolates": isolates,
        "density": density,
        "reciprocity": reciprocity,
    }


def draw_sociogram(names, edge_set, title):
    if not names:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("Matplotlib is required for sociogram rendering") from exc
    fig, ax = plt.subplots(figsize=(7, 7))
    n = len(names)
    positions = {}
    radius = 3
    for i, name in enumerate(names):
        angle = (2 * math.pi * i) / n
        positions[name] = (radius * math.cos(angle), radius * math.sin(angle))

    for a, b in edge_set:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        mutual = (b, a) in edge_set
        color = "#22c55e" if mutual else "#64748b"
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.6, alpha=0.85),
        )

    for name, (x, y) in positions.items():
        ax.scatter([x], [y], s=700, color="#2563eb")
        ax.text(x, y, name, ha="center", va="center", color="white", fontsize=9)

    ax.set_title(title)
    ax.axis("off")
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


@app.context_processor
def inject_common():
    return {"lang": get_lang(), "texts": TEXTS[get_lang()]}


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin_authenticated"] = True
            return redirect(url_for("admin_dashboard", lang=get_lang()))
        flash("Hibás belépési adatok / Invalid login.", "error")
    return render_template("admin_login.html")


@app.get("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    return redirect(url_for("index", lang=get_lang()))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "upload_questionnaire":
                name = request.form.get("name", "").strip()
                file = request.files.get("file")
                questions = parse_questionnaire_excel(file)
                conn.execute(
                    "INSERT INTO questionnaires(name, questions_json, created_at) VALUES(?,?,?)",
                    (name, json.dumps(questions, ensure_ascii=False), datetime.utcnow().isoformat()),
                )
                conn.commit()
                flash("Kérdéssor feltöltve / Questionnaire uploaded.", "success")
            elif action == "upload_roster":
                name = request.form.get("name", "").strip()
                file = request.files.get("file")
                names = parse_roster_excel(file)
                conn.execute(
                    "INSERT INTO rosters(name, names_json, created_at) VALUES(?,?,?)",
                    (name, json.dumps(names, ensure_ascii=False), datetime.utcnow().isoformat()),
                )
                conn.commit()
                flash("Névsor feltöltve / Roster uploaded.", "success")
            elif action == "create_measurement":
                m_name = request.form.get("measurement_name", "").strip()
                questionnaire_id = int(request.form.get("questionnaire_id"))
                roster_id = int(request.form.get("roster_id"))
                identifier = request.form.get("user_identifier", "").strip()
                password = request.form.get("user_password", "")

                q = conn.execute("SELECT * FROM questionnaires WHERE id=?", (questionnaire_id,)).fetchone()
                questions = json.loads(q["questions_json"])
                cur = conn.execute(
                    "INSERT INTO measurements(name, questionnaire_id, roster_id, user_identifier, user_password_hash, created_at) VALUES(?,?,?,?,?,?)",
                    (
                        m_name,
                        questionnaire_id,
                        roster_id,
                        identifier,
                        generate_password_hash(password),
                        datetime.utcnow().isoformat(),
                    ),
                )
                measurement_id = cur.lastrowid
                raw_indices = request.form.get("sociogram_indices", "").strip()
                include_set = set()
                if raw_indices:
                    for part in raw_indices.split(","):
                        part = part.strip()
                        if part.isdigit():
                            include_set.add(int(part) - 1)
                for idx, question in enumerate(questions):
                    include = 1 if idx in include_set else 0
                    conn.execute(
                        "INSERT INTO measurement_questions(measurement_id, question_index, question_text, include_sociogram) VALUES(?,?,?,?)",
                        (measurement_id, idx, question, include),
                    )
                conn.commit()
                flash("Mérés létrehozva / Measurement created.", "success")
        except Exception as exc:
            flash(f"Hiba / Error: {exc}", "error")

    questionnaires = conn.execute("SELECT * FROM questionnaires ORDER BY id DESC").fetchall()
    rosters = conn.execute("SELECT * FROM rosters ORDER BY id DESC").fetchall()
    measurements = conn.execute("SELECT * FROM measurements ORDER BY id DESC").fetchall()
    conn.close()
    return render_template(
        "admin_dashboard.html",
        questionnaires=questionnaires,
        rosters=rosters,
        measurements=measurements,
    )


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        measurement_id = int(request.form.get("measurement_id"))
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        m = conn.execute("SELECT * FROM measurements WHERE id = ?", (measurement_id,)).fetchone()
        conn.close()
        if m and m["user_identifier"] == identifier and check_password_hash(m["user_password_hash"], password):
            session["user_measurement_id"] = measurement_id
            return redirect(url_for("user_questionnaire", lang=get_lang()))
        flash("Hibás adatok / Invalid credentials.", "error")

    conn = get_db()
    measurements = conn.execute("SELECT id, name FROM measurements ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("user_login.html", measurements=measurements)


@app.route("/user/questionnaire", methods=["GET", "POST"])
def user_questionnaire():
    measurement_id = session.get("user_measurement_id")
    if not measurement_id:
        return redirect(url_for("user_login", lang=get_lang()))

    measurement, _, roster, mq = load_measurement(measurement_id)
    names = json.loads(roster["names_json"])

    if request.method == "POST":
        respondent = request.form.get("respondent_name")
        answers = {}
        errors = []

        for item in mq:
            key = str(item["question_index"])
            selected = request.form.getlist(f"q_{item['question_index']}")
            unique_selected = list(dict.fromkeys(selected))
            if respondent in unique_selected:
                errors.append("Magadat nem választhatod / You cannot select yourself.")
            if len(unique_selected) != 3:
                errors.append("Pontosan 3 nevet kell választani / Exactly 3 names are required.")
            answers[key] = unique_selected

        if errors:
            for e in set(errors):
                flash(e, "error")
        else:
            conn = get_db()
            already = conn.execute(
                "SELECT id FROM responses WHERE measurement_id=? AND respondent_name=?",
                (measurement_id, respondent),
            ).fetchone()
            if already:
                flash("Ehhez a névhez már érkezett kitöltés / This respondent has already submitted.", "error")
            else:
                conn.execute(
                    "INSERT INTO responses(measurement_id, respondent_name, answers_json, created_at) VALUES(?,?,?,?)",
                    (measurement_id, respondent, json.dumps(answers, ensure_ascii=False), datetime.utcnow().isoformat()),
                )
                conn.commit()
                flash("Sikeres beküldés / Submission saved.", "success")
            conn.close()

    return render_template("user_questionnaire.html", measurement=measurement, names=names, questions=mq)


@app.get("/admin/results/<int:measurement_id>")
@admin_required
def admin_results(measurement_id):
    measurement, questionnaire, roster, mq = load_measurement(measurement_id)
    if not measurement:
        return redirect(url_for("admin_dashboard", lang=get_lang()))
    names = json.loads(roster["names_json"])

    conn = get_db()
    responses = conn.execute("SELECT * FROM responses WHERE measurement_id = ?", (measurement_id,)).fetchall()
    conn.close()

    question_blocks = []
    for item in mq:
        metrics = compute_metrics(names, responses, item["question_index"])
        question_blocks.append({"item": item, "metrics": metrics})

    return render_template(
        "admin_results.html",
        measurement=measurement,
        questionnaire=questionnaire,
        roster=roster,
        responses=responses,
        question_blocks=question_blocks,
    )


@app.get("/admin/sociogram/<int:measurement_id>/<int:question_index>.png")
@admin_required
def sociogram_png(measurement_id, question_index):
    measurement, _, roster, _ = load_measurement(measurement_id)
    if not measurement:
        return "Not found", 404
    names = json.loads(roster["names_json"])

    conn = get_db()
    responses = conn.execute("SELECT * FROM responses WHERE measurement_id=?", (measurement_id,)).fetchall()
    conn.close()

    metrics = compute_metrics(names, responses, question_index)
    try:
        img = draw_sociogram(names, metrics["edge_set"], f"Q{question_index + 1}")
    except RuntimeError as exc:
        return str(exc), 503
    return send_file(img, mimetype="image/png")


@app.get("/admin/export/excel/<int:measurement_id>")
@admin_required
def export_excel(measurement_id):
    measurement, _, roster, mq = load_measurement(measurement_id)
    names = json.loads(roster["names_json"])

    conn = get_db()
    responses = conn.execute("SELECT * FROM responses WHERE measurement_id=?", (measurement_id,)).fetchall()
    conn.close()

    summary_rows = []
    for item in mq:
        m = compute_metrics(names, responses, item["question_index"])
        summary_rows.append(
            {
                "Question": item["question_text"],
                "Density": round(m["density"], 4),
                "Reciprocity": round(m["reciprocity"], 4),
                "Reciprocal pairs": m["reciprocal_pairs"],
                "Isolates": m["isolates"],
            }
        )

    raw_rows = []
    for row in responses:
        answers = json.loads(row["answers_json"])
        base = {"Respondent": row["respondent_name"], "Submitted": row["created_at"]}
        for item in mq:
            base[item["question_text"]] = ", ".join(answers.get(str(item["question_index"]), []))
        raw_rows.append(base)

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        pd.DataFrame(summary_rows).to_excel(writer, index=False, sheet_name="Summary")
        pd.DataFrame(raw_rows).to_excel(writer, index=False, sheet_name="Responses")
    out.seek(0)
    return send_file(
        out,
        as_attachment=True,
        download_name=f"measurement_{measurement_id}_results.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/admin/export/pdf/<int:measurement_id>")
@admin_required
def export_pdf(measurement_id):
    measurement, _, roster, mq = load_measurement(measurement_id)
    names = json.loads(roster["names_json"])

    conn = get_db()
    responses = conn.execute("SELECT * FROM responses WHERE measurement_id=?", (measurement_id,)).fetchall()
    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Sociometry report / Szociometria riport: {measurement['name']}", styles["Title"]), Spacer(1, 12)]

    for item in mq:
        m = compute_metrics(names, responses, item["question_index"])
        story.append(Paragraph(f"Q{item['question_index'] + 1}: {item['question_text']}", styles["Heading3"]))
        data = [
            ["Density", f"{m['density']:.3f}"],
            ["Reciprocity", f"{m['reciprocity']:.3f}"],
            ["Reciprocal pairs", str(m["reciprocal_pairs"])],
            ["Isolates", str(m["isolates"])],
        ]
        table = Table(data, colWidths=[180, 200])
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"measurement_{measurement_id}_results.pdf", mimetype="application/pdf")


init_db()

if __name__ == "__main__":
    app.run(debug=True)
