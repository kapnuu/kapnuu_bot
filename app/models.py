from app import db


class Data(db.Model):
    __tablename__ = 'data'
    key = db.Column(db.String(32), primary_key=True)
    param = db.Column(db.String(), nullable=True)
    value = db.Column(db.String(), nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)


class BotUser(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer)
    name = db.Column(db.String())
    huify = db.Column(db.Boolean)
    owm_city = db.Column(db.Integer, nullable=True)
    greet = db.Column(db.String, nullable=True)
