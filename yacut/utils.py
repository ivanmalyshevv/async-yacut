import random
import string
from yacut.models import URLMap
from yacut import db

SHORT_ID_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


def get_unique_short_id(length=SHORT_ID_LENGTH):
    """Генерирует уникальный короткий идентификатор."""
    max_attempts = 1000  
    for _ in range(max_attempts):
        short_id = ''.join(random.choices(ALPHABET, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    return get_unique_short_id(length=length+1)
