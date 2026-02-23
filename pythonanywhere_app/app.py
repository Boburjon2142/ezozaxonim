import csv
import io
import os
from collections import Counter
from datetime import date, datetime, timedelta

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, Response
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lifepause_pa.db")

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), default="")
    timezone = db.Column(db.String(64), default="UTC")


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    top1 = db.Column(db.String(255), default="")
    top2 = db.Column(db.String(255), default="")
    top3 = db.Column(db.String(255), default="")
    reflection = db.Column(db.String(800), default="")


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="today")
    estimate_minutes = db.Column(db.Integer, default=25)
    tags = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TimeSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String(80), default="focus")
    source = db.Column(db.String(30), default="manual")


class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    check_date = db.Column(db.Date, nullable=False)
    energy = db.Column(db.Integer, nullable=False)
    stress = db.Column(db.Integer, nullable=False)
    mood = db.Column(db.Integer, nullable=False)
    sleep = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500), default="")


class BreakRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    focus_min = db.Column(db.Integer, default=25)
    break_min = db.Column(db.Integer, default=5)
    long_break_min = db.Column(db.Integer, default=15)
    long_break_every = db.Column(db.Integer, default=4)
    adaptive_enabled = db.Column(db.Boolean, default=True)


class BreakEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_type = db.Column(db.String(30), nullable=False)  # shown, acknowledged, snoozed, ignored
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_schema_compat()

    register_routes(app)
    return app


def ensure_schema_compat() -> None:
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(time_session)")
        cols = [row[1] for row in cursor.fetchall()]
        if "source" not in cols:
            cursor.execute("ALTER TABLE time_session ADD COLUMN source VARCHAR(30) DEFAULT 'manual'")
            conn.commit()
    finally:
        conn.close()


def get_or_create_break_rule(user_id: int) -> BreakRule:
    rule = BreakRule.query.filter_by(user_id=user_id).first()
    if not rule:
        rule = BreakRule(user_id=user_id)
        db.session.add(rule)
        db.session.commit()
    return rule


def safe_int(value: str, fallback: int, min_v: int = 1, max_v: int = 999) -> int:
    try:
        parsed = int(value)
        return max(min_v, min(max_v, parsed))
    except (TypeError, ValueError):
        return fallback


def energy_balance_for_day(user_id: int, day: date) -> float:
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)

    sessions = TimeSession.query.filter(
        TimeSession.user_id == user_id,
        TimeSession.started_at >= start,
        TimeSession.started_at < end,
    ).all()
    focus_minutes = sum(s.duration_minutes for s in sessions)

    check = CheckIn.query.filter_by(user_id=user_id, check_date=day).first()
    energy = check.energy if check else 3
    stress = check.stress if check else 3

    events = BreakEvent.query.filter_by(user_id=user_id, event_date=day).all()
    shown = sum(1 for e in events if e.event_type == "shown")
    ack = sum(1 for e in events if e.event_type == "acknowledged")
    compliance = (ack / shown) if shown else 1.0

    raw = (focus_minutes / 6) + (energy * 8) - (stress * 7) + (compliance * 20)
    return round(max(0.0, min(100.0, raw)), 2)


def week_stats(user_id: int) -> dict:
    days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    sessions = TimeSession.query.filter_by(user_id=user_id).all()
    checks = CheckIn.query.filter_by(user_id=user_id).all()

    by_day_minutes = {d: 0 for d in days}
    for s in sessions:
        d = s.started_at.date()
        if d in by_day_minutes:
            by_day_minutes[d] += s.duration_minutes

    by_day_stress = {d: 3 for d in days}
    by_day_energy = {d: 3 for d in days}
    for c in checks:
        if c.check_date in by_day_stress:
            by_day_stress[c.check_date] = c.stress
            by_day_energy[c.check_date] = c.energy

    trend = [
        {
            "label": d.strftime("%a"),
            "minutes": by_day_minutes[d],
            "stress": by_day_stress[d],
            "energy": by_day_energy[d],
            "score": energy_balance_for_day(user_id, d),
        }
        for d in days
    ]

    tags = Counter([s.tag for s in sessions if s.started_at.date() >= date.today() - timedelta(days=30)])
    top_tags = [{"tag": k, "count": v} for k, v in tags.most_common(5)]

    return {
        "trend": trend,
        "top_tags": top_tags,
        "total_week_min": sum(t["minutes"] for t in trend),
        "avg_stress": round(sum(t["stress"] for t in trend) / len(trend), 2),
        "avg_energy": round(sum(t["energy"] for t in trend) / len(trend), 2),
    }


def get_adaptive_break_hint(user_id: int) -> str:
    check = CheckIn.query.filter_by(user_id=user_id, check_date=date.today()).first()
    rule = get_or_create_break_rule(user_id)
    if not rule.adaptive_enabled:
        return f"Focus {rule.focus_min}m / Break {rule.break_min}m"

    if check and (check.stress >= 4 or check.energy <= 2):
        focus = max(15, rule.focus_min - 5)
        brk = min(20, rule.break_min + 3)
        return f"Adaptive: bugun {focus}m focus + {brk}m break tavsiya qilinadi"

    recent = BreakEvent.query.filter_by(user_id=user_id, event_date=date.today(), event_type="snoozed").count()
    if recent >= 3:
        return "Bugun ko'p snooze bo'ldi. 15-20 daqiqa uzun tanaffus qiling"

    return f"Rhythm yaxshi: {rule.focus_min}m focus / {rule.break_min}m break"


def register_routes(app: Flask) -> None:
    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("today"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            full_name = request.form.get("full_name", "").strip()

            if not email or not password:
                flash("Email va parol majburiy", "error")
                return redirect(url_for("signup"))
            if len(password) < 6:
                flash("Parol kamida 6 belgidan bo'lsin", "error")
                return redirect(url_for("signup"))
            if User.query.filter_by(email=email).first():
                flash("Bu email allaqachon ro'yxatdan o'tgan", "error")
                return redirect(url_for("signup"))

            user = User(email=email, password_hash=generate_password_hash(password), full_name=full_name)
            db.session.add(user)
            db.session.commit()
            get_or_create_break_rule(user.id)
            login_user(user)
            return redirect(url_for("today"))
        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("today"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Login xato", "error")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("today"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("landing"))

    @app.post("/api/session")
    @login_required
    def api_session():
        minutes = safe_int(request.form.get("minutes"), 25, 1, 720)
        tag = (request.form.get("tag") or "focus").strip()[:80]
        source = (request.form.get("source") or "manual").strip()[:30]
        ended = datetime.now()
        started = ended - timedelta(minutes=minutes)

        row = TimeSession(
            user_id=current_user.id,
            started_at=started,
            ended_at=ended,
            duration_minutes=minutes,
            tag=tag,
            source=source,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "minutes": minutes})

    @app.post("/api/break-event")
    @login_required
    def api_break_event():
        event_type = (request.form.get("event_type") or "shown").strip()
        if event_type not in {"shown", "acknowledged", "snoozed", "ignored"}:
            return jsonify({"ok": False}), 400

        db.session.add(BreakEvent(user_id=current_user.id, event_date=date.today(), event_type=event_type))
        db.session.commit()
        return jsonify({"ok": True})

    @app.route("/today", methods=["GET", "POST"])
    @login_required
    def today():
        today_date = date.today()
        plan = Plan.query.filter_by(user_id=current_user.id, plan_date=today_date).first()
        check = CheckIn.query.filter_by(user_id=current_user.id, check_date=today_date).first()
        rule = get_or_create_break_rule(current_user.id)

        if request.method == "POST":
            action = request.form.get("action")

            if action == "save_plan":
                if not plan:
                    plan = Plan(user_id=current_user.id, plan_date=today_date)
                    db.session.add(plan)
                plan.top1 = request.form.get("top1", "").strip()[:255]
                plan.top2 = request.form.get("top2", "").strip()[:255]
                plan.top3 = request.form.get("top3", "").strip()[:255]
                plan.reflection = request.form.get("reflection", "").strip()[:800]
                db.session.commit()
                flash("Plan saqlandi", "ok")

            elif action == "checkin":
                if not check:
                    check = CheckIn(user_id=current_user.id, check_date=today_date, energy=3, stress=3, mood=3, sleep=3)
                    db.session.add(check)
                check.energy = safe_int(request.form.get("energy"), 3, 1, 5)
                check.stress = safe_int(request.form.get("stress"), 3, 1, 5)
                check.mood = safe_int(request.form.get("mood"), 3, 1, 5)
                check.sleep = safe_int(request.form.get("sleep"), 3, 1, 5)
                check.note = request.form.get("note", "").strip()[:500]
                db.session.commit()
                flash("Check-in saqlandi", "ok")

            elif action == "add_task":
                title = request.form.get("task_title", "").strip()
                if title:
                    db.session.add(
                        Task(
                            user_id=current_user.id,
                            plan_date=today_date,
                            title=title[:255],
                            status="today",
                            estimate_minutes=safe_int(request.form.get("estimate_minutes"), 25, 1, 480),
                            tags=request.form.get("tags", "").strip()[:255],
                        )
                    )
                    db.session.commit()
                    flash("Task qo'shildi", "ok")

            elif action == "task_status":
                task_id = safe_int(request.form.get("task_id"), 0, 0, 99999999)
                status = request.form.get("status", "today")
                if status in {"backlog", "today", "done", "blocked"}:
                    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
                    if task:
                        task.status = status
                        db.session.commit()

            elif action == "save_rule":
                rule.focus_min = safe_int(request.form.get("focus_min"), rule.focus_min, 10, 90)
                rule.break_min = safe_int(request.form.get("break_min"), rule.break_min, 3, 30)
                rule.long_break_min = safe_int(request.form.get("long_break_min"), rule.long_break_min, 10, 45)
                rule.long_break_every = safe_int(request.form.get("long_break_every"), rule.long_break_every, 2, 8)
                rule.adaptive_enabled = request.form.get("adaptive_enabled") == "on"
                db.session.commit()
                flash("Break rule yangilandi", "ok")

            return redirect(url_for("today"))

        sessions = (
            TimeSession.query.filter_by(user_id=current_user.id)
            .order_by(TimeSession.started_at.desc())
            .limit(12)
            .all()
        )
        tasks = Task.query.filter_by(user_id=current_user.id, plan_date=today_date).order_by(Task.created_at.desc()).all()

        total_today = sum(s.duration_minutes for s in sessions if s.started_at.date() == today_date)
        done_today = sum(1 for t in tasks if t.status == "done")
        score = energy_balance_for_day(current_user.id, today_date)
        break_hint = get_adaptive_break_hint(current_user.id)

        return render_template(
            "today.html",
            plan=plan,
            check=check,
            sessions=sessions,
            tasks=tasks,
            score=score,
            total_today=total_today,
            done_today=done_today,
            rule=rule,
            break_hint=break_hint,
        )

    @app.route("/plans", methods=["GET", "POST"])
    @login_required
    def plans():
        if request.method == "POST":
            action = request.form.get("action")
            if action == "add":
                title = request.form.get("title", "").strip()
                if title:
                    db.session.add(
                        Task(
                            user_id=current_user.id,
                            plan_date=date.today(),
                            title=title[:255],
                            status=request.form.get("status", "backlog"),
                            estimate_minutes=safe_int(request.form.get("estimate_minutes"), 25, 1, 480),
                            tags=request.form.get("tags", "").strip()[:255],
                        )
                    )
                    db.session.commit()
            elif action == "move":
                task_id = safe_int(request.form.get("task_id"), 0, 0, 99999999)
                to_status = request.form.get("to_status", "today")
                if to_status in {"backlog", "today", "done", "blocked"}:
                    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
                    if task:
                        task.status = to_status
                        db.session.commit()
            return redirect(url_for("plans"))

        all_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(200).all()
        columns = {
            "backlog": [t for t in all_tasks if t.status == "backlog"],
            "today": [t for t in all_tasks if t.status == "today"],
            "done": [t for t in all_tasks if t.status == "done"],
            "blocked": [t for t in all_tasks if t.status == "blocked"],
        }
        return render_template("plans.html", columns=columns)

    @app.route("/time", methods=["GET", "POST"])
    @login_required
    def time_log():
        if request.method == "POST":
            mins = safe_int(request.form.get("minutes"), 25, 1, 720)
            tag = request.form.get("tag", "focus").strip()[:80]
            source = request.form.get("source", "manual").strip()[:30]
            end = datetime.now()
            start = end - timedelta(minutes=mins)
            row = TimeSession(user_id=current_user.id, started_at=start, ended_at=end, duration_minutes=mins, tag=tag, source=source)
            db.session.add(row)
            db.session.commit()
            flash("Session qo'shildi", "ok")
            return redirect(url_for("time_log"))

        rows = TimeSession.query.filter_by(user_id=current_user.id).order_by(TimeSession.started_at.desc()).all()
        total_today = sum(r.duration_minutes for r in rows if r.started_at.date() == date.today())
        total_week = sum(r.duration_minutes for r in rows if r.started_at.date() >= date.today() - timedelta(days=6))
        tags = Counter([r.tag for r in rows[:300]])
        return render_template("time.html", rows=rows, total_today=total_today, total_week=total_week, tags=tags)

    @app.route("/insights")
    @login_required
    def insights():
        stats = week_stats(current_user.id)
        score = energy_balance_for_day(current_user.id, date.today())
        recommendation = "Rhythm barqaror, davom eting."
        if score < 45:
            recommendation = "Stressni pasaytirish uchun focus blokni qisqartiring va breakni ko'paytiring."
        elif stats["avg_stress"] >= 4:
            recommendation = "Stress yuqori trendda. Tushlikdan keyin 15 daqiqa yurish break qo'shing."

        return render_template(
            "insights.html",
            stats=stats,
            score=score,
            recommendation=recommendation,
        )

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        rule = get_or_create_break_rule(current_user.id)
        if request.method == "POST":
            current_user.full_name = request.form.get("full_name", "").strip()[:120]
            current_user.timezone = request.form.get("timezone", "UTC").strip()[:64]
            rule.focus_min = safe_int(request.form.get("focus_min"), rule.focus_min, 10, 90)
            rule.break_min = safe_int(request.form.get("break_min"), rule.break_min, 3, 30)
            rule.long_break_min = safe_int(request.form.get("long_break_min"), rule.long_break_min, 10, 45)
            rule.long_break_every = safe_int(request.form.get("long_break_every"), rule.long_break_every, 2, 8)
            rule.adaptive_enabled = request.form.get("adaptive_enabled") == "on"
            db.session.commit()
            flash("Sozlamalar saqlandi", "ok")
            return redirect(url_for("settings"))

        return render_template("settings.html", rule=rule)

    @app.route("/export/csv")
    @login_required
    def export_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["type", "date", "value1", "value2", "value3"])

        for s in TimeSession.query.filter_by(user_id=current_user.id).order_by(TimeSession.started_at.desc()).limit(500):
            writer.writerow(["session", s.started_at.isoformat(), s.duration_minutes, s.tag, s.source])

        for c in CheckIn.query.filter_by(user_id=current_user.id).order_by(CheckIn.check_date.desc()).limit(500):
            writer.writerow(["checkin", c.check_date.isoformat(), c.energy, c.stress, c.mood])

        for t in Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(500):
            writer.writerow(["task", t.plan_date.isoformat(), t.title, t.status, t.estimate_minutes])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=lifepause_export.csv"},
        )


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
