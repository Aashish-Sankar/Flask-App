from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aashish app'
    app.config["SECRET_KEY"] = "aashish_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .views import views
    from .auth import auth
    
    from . import models

    login_manager = LoginManager()
    login_manager.login_view = 'auth.admin_login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    



    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    with app.app_context():
        db.create_all()

    return app

