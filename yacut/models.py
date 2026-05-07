from datetime import datetime, timezone
import random
import string
from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def get_unique_short_id(cls, length=6):
        alphabet = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(random.choices(alphabet, k=length))
            if not cls.query.filter_by(short=short_id).first():
                return short_id