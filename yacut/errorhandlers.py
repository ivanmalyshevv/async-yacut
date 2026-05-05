from flask import render_template, jsonify, request

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Страница не найдена'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
        return render_template('500.html'), 500