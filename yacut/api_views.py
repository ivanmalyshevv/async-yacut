import re
from flask import Blueprint, request, jsonify, url_for
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut import db

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/id/', methods=['POST'])
def create_short_url():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400

    if 'url' not in data:
        return jsonify({'message': '"url" является обязательным полем!'}), 400

    original = data['url']

    if not original or not original.strip():
        return jsonify({'message': '"url" является обязательным полем!'}), 400

    custom_id = data.get('custom_id')
    allowed_pattern = re.compile(r'^[a-zA-Z0-9]{1,16}$')

    if custom_id:
        if custom_id == 'files':
            return jsonify({
                'message': 'Предложенный вариант короткой ссылки уже '
                           'существует.'
            }), 400

        if not allowed_pattern.match(custom_id):
            return jsonify({
                'message': 'Указано недопустимое имя для короткой ссылки'
            }), 400

        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify({
                'message': 'Предложенный вариант короткой ссылки уже '
                           'существует.'
            }), 400

        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': original,
        'short_link': url_for('main.follow_short', short=short_id,
                              _external=True)
    }), 201


@api_bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original}), 200