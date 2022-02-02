from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

database = SQLAlchemy()
DB_NAME = "alimconfiance"

def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = 'somethingbig'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:password@localhost/{DB_NAME}' #f'sqlite:///{DB_NAME}' # mysql://username:password@server/db
    database.init_app(app)
    
    from .views import views
    app.register_blueprint(views, url_prefix='/')
    
    from . import models2
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return models2.Inspecteur.query.get(int(id))
    
    
    return app

def create_database(app):
    pass
    # Uniquement utile pour les base .db et .sqlite en loca
    ###
    # if not path.exists('website/' + DB_NAME):
    #     database.create_all(app=app)
    #     print('Created Database!')