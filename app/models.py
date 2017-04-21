from app import db


class Data(db.Model):
    __tablename__ = 'data'
    key = db.Column(db.String(32), primary_key=True)
    param = db.Column(db.String(), nullable=True)
    value = db.Column(db.String(), nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)
