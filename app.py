from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
import mysql.connector


connection = mysql.connector.connect(host='yury.mysql.database.azure.com', port='3306', database='correo_yury',user='AAncamilla', password='manchester12,')
cursor = connection.cursor()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.secret_key="clave muuuy secreta"

    db.init_app(app)

    migrate = Migrate(app, db)
    from routes import register_routes, bp_jefe_rrhh, bp as personal_rrhh_bp
    register_routes(app, db)
    app.register_blueprint(personal_rrhh_bp)
    app.register_blueprint(bp_jefe_rrhh)

   
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
   # app.register_blueprint(auth, url_prefix='/auth')

    from models import Usuario 
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app

