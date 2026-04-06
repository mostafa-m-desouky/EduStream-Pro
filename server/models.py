from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    gender = db.Column(db.String(10)) # Male, Female
    profile_pic = db.Column(db.String(255), nullable=False, default='default.jpg')
   
    courses = db.relationship('Course', backref= 'author', lazy=True, cascade="all, delete-orphan")

    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade="all, delete-orphan")
    
    payments = db.relationship('Payment', backref='payer', lazy=True, cascade="all, delete-orphan")

 
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_hours = db.Column(db.Integer)
    thumbnail = db.Column(db.String(255), nullable=False, default='default_course.jpg')

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade="all, delete-orphan")
    course_enrollments = db.relationship('Enrollment', backref='enrolled_course', lazy=True)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    
    # 3. Status Of Payment
    # Status (Pending, Succeeded, Failed) - Default: Pending
    status = db.Column(db.String(20), default='pending')
    
    # 4. Type Of Payment
    # 'Credit Card', 'Vodafone Cash', 'Fawry', 'Promo Code'
    payment_method = db.Column(db.String(50), nullable=False)
    
    currency = db.Column(db.String(10), default='EGP')
        
    # Payment Date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)