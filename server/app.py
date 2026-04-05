from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User, Course, Lesson, Payment, Enrollment
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
# Redirects to /login if not logged in
login_manager.login_view = 'auth.login'

@app.route('/')
def index():
    return "LearnFlow API is Running!"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

from routes import auth
app.register_blueprint(auth.auth, url_prefix='/api/auth')

if __name__ == '__main__':
    app.run(debug=True)