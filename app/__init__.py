from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import create_engine

from app.models.user import User
from app.seeder import seed
from config import Config
from app.extensions import db, create_session

mail = Mail()
app = Flask(__name__)


def create_app(config_class=Config):
    app.config.from_object(config_class)
    mail.init_app(app)
    app.app_context().push()
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    app.app_context().push()
    engine = create_engine('sqlite:///714_street.db?check_same_thread=False')
    db.metadata.create_all(engine)
    db_session = create_session()

    if len(db_session.query(User).all()) == 0:
        seed()
        db_session.close()

    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        db = create_session()
        user = db.query(User).get(user_id)
        db.close()
        return user

    return app
