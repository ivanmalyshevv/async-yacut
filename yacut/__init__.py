from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__,
                static_folder='../html',
                static_url_path='',
                template_folder='../html')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 'sqlite:///yacut.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    from .views import main_bp
    app.register_blueprint(main_bp)

    from .api_views import api_bp
    app.register_blueprint(api_bp)

    from .errorhandlers import register_error_handlers
    register_error_handlers(app)
    return app


app = create_app()