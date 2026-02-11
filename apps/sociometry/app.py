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


def switch_lang_url(to_lang: str):
    args = request.args.to_dict(flat=True)
    args["lang"] = to_lang
    endpoint = request.endpoint or "index"
    values = (request.view_args or {}).copy()
    return url_for(endpoint, **values, **args)


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


def _safe_div(num, den):
    return num / den if den else 0.0


def _stddev(values):
    vals = list(values)
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return math.sqrt(var)


def _compute_layout(names, undirected_weights):
    n = len(names)
    if n == 0:
        return {}
    if n == 1:
        return {names[0]: (0.0, 0.0)}

    positions = {}
    radius = 4.0
    for i, name in enumerate(names):
        angle = (2 * math.pi * i) / n
        positions[name] = [radius * math.cos(angle), radius * math.sin(angle)]

    step = 0.04
    min_dist = 0.001
    for _ in range(140):
        disp = {name: [0.0, 0.0] for name in names}

        for i, a in enumerate(names):
            xa, ya = positions[a]
            for b in names[i + 1 :]:
                xb, yb = positions[b]
                dx = xa - xb
                dy = ya - yb
                dist = math.sqrt(dx * dx + dy * dy) + min_dist
                force = 0.08 / dist
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                disp[a][0] += fx
                disp[a][1] += fy
                disp[b][0] -= fx
                disp[b][1] -= fy

        for (a, b), w in undirected_weights.items():
            xa, ya = positions[a]
            xb, yb = positions[b]
            dx = xb - xa
            dy = yb - ya
            dist = math.sqrt(dx * dx + dy * dy) + min_dist
            target = max(0.8, 2.8 - min(w, 6) * 0.28)
            force = 0.05 * w * (dist - target)
            fx = (dx / dist) * force
            fy = (dy / dist) * force
            disp[a][0] += fx
            disp[a][1] += fy
            disp[b][0] -= fx
            disp[b][1] -= fy

        for name in names:
            positions[name][0] += disp[name][0] * step
            positions[name][1] += disp[name][1] * step

        cx = sum(positions[nm][0] for nm in names) / n
        cy = sum(positions[nm][1] for nm in names) / n
        for name in names:
            positions[name][0] -= cx
            positions[name][1] -= cy

    return {k: tuple(v) for k, v in positions.items()}


def compute_metrics_for_questions(names, responses, question_indexes):
    in_degree = {name: 0 for name in names}
    out_degree = {name: 0 for name in names}
    edge_set = set()
    edge_set_by_q = {q: set() for q in question_indexes}

    for row in responses:
        sender = row["respondent_name"]
        answers = json.loads(row["answers_json"])
        sender_targets = set()

        for q_idx in question_indexes:
            selected = answers.get(str(q_idx), [])
            for target in selected:
                if sender == target:
                    continue
                if target in in_degree:
                    edge_set.add((sender, target))
                    edge_set_by_q[q_idx].add((sender, target))
                    sender_targets.add(target)

        if sender in out_degree:
            out_degree[sender] = len(sender_targets)

    for _, target in edge_set:
        in_degree[target] += 1

    reciprocal_pairs = 0
    reciprocal_levels = {}
    reciprocal_nodes = set()
    undirected_weights = {}

    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            pair = (a, b)
            mutual_count = 0
            directional_count = 0
            for q_idx in question_indexes:
                q_edges = edge_set_by_q[q_idx]
                ab = (a, b) in q_edges
                ba = (b, a) in q_edges
                if ab:
                    directional_count += 1
                if ba:
                    directional_count += 1
                if ab and ba:
                    mutual_count += 1
            if mutual_count > 0:
                reciprocal_pairs += 1
                reciprocal_levels[pair] = mutual_count
                reciprocal_nodes.add(a)
                reciprocal_nodes.add(b)
            if directional_count > 0:
                undirected_weights[pair] = directional_count + (2 * mutual_count)

    neighbors = {name: set() for name in names}
    for a, b in edge_set:
        neighbors[a].add(b)
        neighbors[b].add(a)

    k_triad = 0
    for a, b in edge_set:
        if (neighbors[a] & neighbors[b]) - {a, b}:
            k_triad += 1

    k_ossz = len(edge_set)
    n = len(names)
    ki = _safe_div(reciprocal_pairs, k_ossz)
    vk = _safe_div(2 * reciprocal_pairs, k_ossz)
    ji1 = ki
    ji2 = _safe_div(k_triad, k_ossz)
    si = _safe_div(k_ossz, n * (n - 1)) if n > 1 else 0.0
    koh = _safe_div(reciprocal_pairs, (n * (n - 1) / 2)) if n > 1 else 0.0
    cm = _safe_div(len(reciprocal_nodes), n)
    sd_rokonszenvi = _stddev(in_degree.values())
    sd_funkcionalis = _stddev(out_degree.values())
    csoportlegkor = _safe_div(sd_rokonszenvi, sd_funkcionalis) if sd_funkcionalis else None

    isolates = sum(1 for nm in names if in_degree[nm] == 0 and out_degree[nm] == 0)
    reciprocity = _safe_div(reciprocal_pairs, k_ossz)

    return {
        "in_degree": in_degree,
        "out_degree": out_degree,
        "edge_set": edge_set,
        "edge_set_by_q": edge_set_by_q,
        "reciprocal_pairs": reciprocal_pairs,
        "reciprocal_levels": reciprocal_levels,
        "reciprocal_nodes": reciprocal_nodes,
        "undirected_weights": undirected_weights,
        "isolates": isolates,
        "density": si,
        "reciprocity": reciprocity,
        "k_ossz": k_ossz,
        "k_kolcs": reciprocal_pairs,
        "k_triad": k_triad,
        "KI": ki,
        "VK": vk,
        "JI1": ji1,
        "JI2": ji2,
        "SI": si,
        "KOH": koh,
        "CM": cm,
        "SD_rokonszenvi": sd_rokonszenvi,
        "SD_funkcionalis": sd_funkcionalis,
        "Csoportlegkor": csoportlegkor,
    }


def compute_metrics(names, responses, question_index):
    return compute_metrics_for_questions(names, responses, [question_index])


def compute_combined_metrics(names, responses, question_indexes):
    return compute_metrics_for_questions(names, responses, question_indexes)


def classify_significance(name, sympathy_in, functional_in):
    score = (2 * sympathy_in) + functional_in
    if score >= 8:
        return "Elsődleges / Primary"
    if score >= 4:
        return "Másodlagos / Secondary"
    return "Periférikus / Peripheral"


def build_name_summary_rows(names, mq, sympathy_metrics, functional_metrics):
    rows = []
    sympathy_q = [item for item in mq if item["include_sociogram"]]
    functional_q = [item for item in mq if not item["include_sociogram"]]

    sympathy_in = sympathy_metrics["in_degree"] if sympathy_metrics else {n: 0 for n in names}
    functional_in = functional_metrics["in_degree"] if functional_metrics else {n: 0 for n in names}

    for name in names:
        row = {"Név / Name": name}
        total = 0

        row["Rokonszenvi választások"] = sympathy_in.get(name, 0)
        total += row["Rokonszenvi választások"]

        row["Funkcióválasztások"] = functional_in.get(name, 0)
        total += row["Funkcióválasztások"]

        row["Összesen / Total"] = total
        row["Jelentőség"] = classify_significance(name, row["Rokonszenvi választások"], row["Funkcióválasztások"])
        rows.append(row)
    return rows


def build_name_question_breakdown(names, responses, mq):
    rows = []
    per_question_metrics = {item["question_index"]: compute_metrics(names, responses, item["question_index"]) for item in mq}
    for name in names:
        row = {"Név / Name": name}
        total = 0
        for item in mq:
            val = per_question_metrics[item["question_index"]]["in_degree"].get(name, 0)
            row[f"Q{item['question_index'] + 1}"] = val
            total += val
        row["Összesen / Total"] = total
        rows.append(row)
    return rows


def metrics_row(label, metrics):
    return {
        "Hálózat / Network": label,
        "KI": round(metrics["KI"], 4),
        "VK": round(metrics["VK"], 4),
        "JI1": round(metrics["JI1"], 4),
        "JI2": round(metrics["JI2"], 4),
        "SI": round(metrics["SI"], 4),
        "KOH": round(metrics["KOH"], 4),
        "CM": round(metrics["CM"], 4),
        "SD_rokonszenvi": round(metrics["SD_rokonszenvi"], 4),
        "SD_funkcionalis": round(metrics["SD_funkcionalis"], 4),
        "Csoportlegkor": round(metrics["Csoportlegkor"], 4) if metrics["Csoportlegkor"] is not None else None,
        "Reciprocal pairs": metrics["reciprocal_pairs"],
        "Isolates": metrics["isolates"],
    }


def draw_sociogram(names, metrics, title):
    if not names:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except Exception as exc:
        raise RuntimeError("Matplotlib is required for sociogram rendering") from exc

    edge_set = metrics["edge_set"]
    reciprocal_levels = metrics.get("reciprocal_levels", {})
    positions = _compute_layout(names, metrics.get("undirected_weights", {}))

    fig, ax = plt.subplots(figsize=(9, 7))
    mutual_color_map = {1: "#22c55e", 2: "#f59e0b", 3: "#ef4444"}

    for a, b in sorted(edge_set):
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        mutual = (b, a) in edge_set

        if mutual:
            pair = tuple(sorted((a, b)))
            level = min(reciprocal_levels.get(pair, 1), 3)
            color = mutual_color_map[level]
            rad = 0.16 if a < b else -0.16
            lw = 1.7 + (0.4 * level)
        else:
            color = "#64748b"
            rad = 0.0
            lw = 1.4

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="->",
                color=color,
                lw=lw,
                alpha=0.9,
                shrinkA=20,
                shrinkB=20,
                connectionstyle=f"arc3,rad={rad}",
            ),
        )

    in_degree = metrics.get("in_degree", {})
    max_in = max(in_degree.values()) if in_degree else 1
    for name in names:
        x, y = positions[name]
        strength = in_degree.get(name, 0) / max(max_in, 1)
        node_color = (1.0, 0.95 - 0.45 * strength, 0.65 - 0.45 * strength)
        ax.scatter([x], [y], s=1200, color=node_color, edgecolors="#111827", linewidths=1.6, zorder=3)
        ax.text(x, y + 0.18, name, ha="center", va="center", color="#111827", fontsize=9, fontweight="bold", zorder=4)

    legend_items = [
        Line2D([0], [0], color="#64748b", lw=1.6, label="Egyirányú választás / One-way"),
        Line2D([0], [0], color=mutual_color_map[1], lw=2.0, label="1× kölcsönös / 1× mutual"),
        Line2D([0], [0], color=mutual_color_map[2], lw=2.4, label="2× kölcsönös / 2× mutual"),
        Line2D([0], [0], color=mutual_color_map[3], lw=2.8, label="3×+ kölcsönös / 3×+ mutual"),
    ]
    ax.legend(handles=legend_items, loc="upper right", frameon=True)

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
    return {"lang": get_lang(), "texts": TEXTS[get_lang()], "switch_lang_url": switch_lang_url}


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

    selected_answers = {}
    selected_respondent = ""

    if request.method == "POST":
        respondent = request.form.get("respondent_name")
        selected_respondent = respondent or ""
        answers = {}
        errors = []

        for item in mq:
            key = str(item["question_index"])
            selected = request.form.getlist(f"q_{item['question_index']}")
            unique_selected = list(dict.fromkeys(selected))
            selected_answers[key] = unique_selected
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
                selected_answers = {}
                selected_respondent = ""
                flash("Sikeres beküldés / Submission saved.", "success")
            conn.close()

    return render_template(
        "user_questionnaire.html",
        measurement=measurement,
        names=names,
        questions=mq,
        selected_answers=selected_answers,
        selected_respondent=selected_respondent,
    )


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

    selected_indices = [item["question_index"] for item in mq if item["include_sociogram"]]
    functional_indices = [item["question_index"] for item in mq if not item["include_sociogram"]]

    sympathy_metrics = compute_combined_metrics(names, responses, selected_indices) if selected_indices else compute_metrics_for_questions(names, responses, [])
    functional_metrics = compute_combined_metrics(names, responses, functional_indices) if functional_indices else compute_metrics_for_questions(names, responses, [])

    selected_indices_display = [idx + 1 for idx in selected_indices]
    functional_indices_display = [idx + 1 for idx in functional_indices]

    combined_metrics = compute_combined_metrics(names, responses, selected_indices) if selected_indices else None
    aggregate_rows = []
    if selected_indices:
        aggregate_rows.append(metrics_row("Rokonszenvi háló", sympathy_metrics))
    if functional_indices:
        aggregate_rows.append(metrics_row("Funkcióháló", functional_metrics))
    if selected_indices and functional_indices:
        all_metrics = compute_combined_metrics(names, responses, selected_indices + functional_indices)
        aggregate_rows.append(metrics_row("Teljes háló", all_metrics))

    question_blocks = [{"item": item} for item in mq]
    name_summary_rows = build_name_summary_rows(names, mq, sympathy_metrics, functional_metrics)
    name_question_breakdown = build_name_question_breakdown(names, responses, mq)

    return render_template(
        "admin_results.html",
        measurement=measurement,
        questionnaire=questionnaire,
        roster=roster,
        responses=responses,
        question_blocks=question_blocks,
        selected_indices=selected_indices,
        selected_indices_display=selected_indices_display,
        functional_indices=functional_indices,
        functional_indices_display=functional_indices_display,
        combined_metrics=combined_metrics,
        aggregate_rows=aggregate_rows,
        name_summary_rows=name_summary_rows,
        name_question_breakdown=name_question_breakdown,
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
        img = draw_sociogram(names, metrics, f"Q{question_index + 1}")
    except RuntimeError as exc:
        return str(exc), 503
    return send_file(img, mimetype="image/png")


@app.get("/admin/sociogram/combined/<int:measurement_id>.png")
@admin_required
def sociogram_combined_png(measurement_id):
    measurement, _, roster, mq = load_measurement(measurement_id)
    if not measurement:
        return "Not found", 404
    names = json.loads(roster["names_json"])

    selected_indices = [item["question_index"] for item in mq if item["include_sociogram"]]
    if not selected_indices:
        return "No sociogram indices selected", 400

    conn = get_db()
    responses = conn.execute("SELECT * FROM responses WHERE measurement_id=?", (measurement_id,)).fetchall()
    conn.close()

    metrics = compute_combined_metrics(names, responses, selected_indices)
    try:
        label = ",".join(str(i + 1) for i in selected_indices)
        img = draw_sociogram(names, metrics, f"Combined Q: {label}")
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

    selected_indices = [item["question_index"] for item in mq if item["include_sociogram"]]
    functional_indices = [item["question_index"] for item in mq if not item["include_sociogram"]]

    summary_rows = []
    if selected_indices:
        sympathy_metrics = compute_combined_metrics(names, responses, selected_indices)
        summary_rows.append(metrics_row("Rokonszenvi háló", sympathy_metrics))
    else:
        sympathy_metrics = compute_metrics_for_questions(names, responses, [])

    if functional_indices:
        functional_metrics = compute_combined_metrics(names, responses, functional_indices)
        summary_rows.append(metrics_row("Funkcióháló", functional_metrics))
    else:
        functional_metrics = compute_metrics_for_questions(names, responses, [])

    if selected_indices and functional_indices:
        all_metrics = compute_combined_metrics(names, responses, selected_indices + functional_indices)
        summary_rows.append(metrics_row("Teljes háló", all_metrics))

    raw_rows = []
    for row in responses:
        answers = json.loads(row["answers_json"])
        base = {"Respondent": row["respondent_name"], "Submitted": row["created_at"]}
        for item in mq:
            base[item["question_text"]] = ", ".join(answers.get(str(item["question_index"]), []))
        raw_rows.append(base)

    out = io.BytesIO()
    name_summary_rows = build_name_summary_rows(names, mq, sympathy_metrics, functional_metrics)
    name_question_breakdown = build_name_question_breakdown(names, responses, mq)

    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        pd.DataFrame(summary_rows).to_excel(writer, index=False, sheet_name="Summary")
        pd.DataFrame(raw_rows).to_excel(writer, index=False, sheet_name="Responses")
        pd.DataFrame(name_summary_rows).to_excel(writer, index=False, sheet_name="Name summary")
        pd.DataFrame(name_question_breakdown).to_excel(writer, index=False, sheet_name="Question breakdown")
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
