from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

db = SQLAlchemy()


def create_app():
    base_dir = Path(__file__).resolve().parent.parent
    html_dir = base_dir / 'html'
    
    app = Flask(
        __name__,
        template_folder=str(html_dir),
        static_folder=str(html_dir),
        static_url_path=''
    )
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 'sqlite:///yacut.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DISK_TOKEN'] = os.getenv('DISK_TOKEN')

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