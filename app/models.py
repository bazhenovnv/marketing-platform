from datetime import datetime
from .extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))

    bots = db.relationship("Bot", backref="owner")


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    subscribers = db.relationship("Subscriber", backref="bot")


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(100))
    username = db.Column(db.String(100))
    bot_id = db.Column(db.Integer, db.ForeignKey("bot.id"))


class Broadcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bot_id = db.Column(db.Integer, db.ForeignKey("bot.id"))


class BroadcastLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    error = db.Column(db.Text)

    subscriber_id = db.Column(db.Integer)
    broadcast_id = db.Column(db.Integer)