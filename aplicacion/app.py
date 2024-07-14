from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
    from routes import register_routes
    register_routes(app, db)
    return app

