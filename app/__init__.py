from flask import Flask,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from .config import DB_PATH
db= SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='BISMILLAHIRRAHMANIRRAHIM123'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
        
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    
    from .models import User,Note
    
    create_database(app)
    
    
    login_manager = LoginManager()
    login_manager.login_view='auth.login'
    login_manager.init_app(app)
    
    
    @login_manager.user_loader
    #buradan sonra önemli bir hata aldık latin 1 yani hashleme utf-8 karakterlerini tanımadığı için hata veriyordu hemen flask login /utils.py altındaki key= key.encode()
    def load_user(id):
        return User.query.get(int(id))
    from werkzeug.exceptions import RequestEntityTooLarge

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        flash('Dosya boyutu en fazla 10 MB olabilir.', 'error')
        return redirect(url_for('views.home'))
    return app
    
def create_database(app):
    if not path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            print('Created Database')
