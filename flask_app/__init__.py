from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from flask_app import routes
