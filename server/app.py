from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User, Course, Lesson, Payment, Enrollment

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return "LearnFlow API is Running!"

from routes import auth
app.register_blueprint(auth.auth)

if __name__ == '__main__':
    app.run(debug=True)