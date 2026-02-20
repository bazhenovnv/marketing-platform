from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import User, Bot, Subscriber, Broadcast
from .extensions import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .telegram_service import TelegramService
from .broadcast_service import send_broadcast

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect(url_for("main.login"))


# ---------- AUTH ----------

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("main.login"))

    return render_template("login.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.login"))


# ---------- DASHBOARD ----------

@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    if request.method == "POST":
        bot = Bot(token=request.form["token"], user_id=current_user.id)
        db.session.add(bot)
        db.session.commit()

    bot = Bot.query.filter_by(user_id=current_user.id).first()
    subscribers = bot.subscribers if bot else []

    return render_template("dashboard.html",
                           bot=bot,
                           subscriber_count=len(subscribers))


# ---------- BROADCAST ----------

@main.route("/broadcast", methods=["GET", "POST"])
@login_required
def broadcast():

    bot = Bot.query.filter_by(user_id=current_user.id).first()

    if not bot:
        return "Добавьте бота"

    subscribers = bot.subscribers

    if request.method == "POST":

        broadcast = Broadcast(
            text=request.form["message"],
            bot_id=bot.id
        )

        db.session.add(broadcast)
        db.session.commit()

        telegram = TelegramService(bot.token)

        sent, failed = send_broadcast(bot, broadcast, subscribers, telegram)

        return f"Отправлено: {sent}, Ошибок: {failed}"

    return render_template("broadcast.html", total=len(subscribers))


# ---------- WEBHOOK ----------

@main.route("/webhook/<int:bot_id>", methods=["POST"])
def webhook(bot_id):

    bot = Bot.query.get(bot_id)
    if not bot:
        return "bot not found"

    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        username = data["message"]["chat"].get("username")

        exists = Subscriber.query.filter_by(
            telegram_id=chat_id,
            bot_id=bot.id
        ).first()

        if not exists:
            sub = Subscriber(
                telegram_id=chat_id,
                username=username,
                bot_id=bot.id
            )
            db.session.add(sub)
            db.session.commit()

    return jsonify({"ok": True})