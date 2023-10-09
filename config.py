# config.py

from flask import Flask
import os

app = Flask(__name__)
app.secret_key = "AppDev1Project"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static')
app.config['PERMANENT_SESSION_LIFETIME'] = 1800
