from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'my_secrect_word'

db = SQLAlchemy(app)

migrate = Migrate(app, db)
CORS(app)


from src import routes, models