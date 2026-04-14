from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User
from flask_cors import CORS
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
# Redirects to /login if not logged in
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return {
        "status": "error",
        "message": "Please log in to access this page."
    }, 401

from routes.main import main
from routes.auth import auth
from routes.courses import courses
from routes.lessons import lessons
from routes.enrollments import enrollments
from routes.payments import payments

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(courses, url_prefix='/api/courses')
app.register_blueprint(lessons, url_prefix='/api/lessons')
app.register_blueprint(enrollments, url_prefix='/api/enrollments')
app.register_blueprint(payments, url_prefix='/api/payments')

if __name__ == '__main__':
    app.run(debug=True)