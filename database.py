from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    image_path = db.Column(db.String(255))
    wine_name = db.Column(db.String(255))
    producer = db.Column(db.String(255))
    vintage = db.Column(db.String(10))
    region = db.Column(db.String(255))
    country = db.Column(db.String(255))
    grape_variety = db.Column(db.String(255))
    other_details = db.Column(db.Text)
    confidence = db.Column(db.Float, default=0.0)
    raw_ai_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}