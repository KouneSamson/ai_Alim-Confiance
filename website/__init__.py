from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

database = SQLAlchemy()
DB_NAME = "alim.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'somethingbig'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # mysql://username:password@server/db 
    database.init_app(app)
    
    from .views import views
    app.register_blueprint(views, url_prefix='/')
    
    from . import models
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        database.create_all(app=app)
        print('Created Database!')