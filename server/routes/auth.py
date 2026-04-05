from flask import (Blueprint, request, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from utils import media_handlers
from flask_login import login_user, logout_user, login_required, current_user


auth = Blueprint('auth', __name__)

ALLOWED_ROLES = ['student', 'teacher']

@auth.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return {
            "status": "info",
            "message": "You already have an account and you are logged in!"
        }, 200
    # Using request.form and request.files instead of get_json() 
    # because the request contains binary data (profile picture) request.get_json().

    username = request.form.get('username').strip().title()
    email = request.form.get('email').strip()

    # Note: We are NOT using .strip() on the password intentionally.
    # Passwords can legitimately contain leading or trailing spaces as part 
    # of a complex passphrase. Trimming them could lower entropy and 
    # mismatch the user's intended secret.
    raw_password = request.form.get('password')
    role = request.form.get('role', 'student').lower().strip()
    gender = request.form.get('gender')


    if not username:
        return {"error": "Username cannot be empty"}, 400

    if db.session.query(User).filter_by(email=email).first():
            return {
                 'status': "error",
                 'message': "This Email Already Exist"
            }, 409
    
    if not raw_password or len(raw_password) < 6:
        return {"error": "Password is too short (min 6 characters)"}, 400
    
    hashed_password = generate_password_hash(raw_password, method='scrypt')

    if gender not in ['male', 'female']:
        return {"error": "Invalid gender value"}, 400
    
    if role not in ALLOWED_ROLES:
        return {
            "status": "error",
            "message": f"Invalid role. Allowed roles are: {', '.join(ALLOWED_ROLES)}"
        }, 400
    

    # If pic_name is None, the database will automatically use the 
    # 'default.jpg' defined in the User Model.

    if 'profile_pic' in request.files and request.files['profile_pic'].filename != '':
        pic_name = media_handlers.save_picture(request.files['profile_pic'])
    else:
        pic_name = 'male_default.png' if gender == 'male' else 'female_default.png'

    user = User(
        username = username,
        email = email,
        password = hashed_password,
        role = role,
        gender = gender,
        profile_pic = pic_name
    )

    try:
        db.session.add(user)
        db.session.commit()
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user.id
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not register user. Database error."}, 500
    

@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return {
            "status": "info",
            "message": "You are already logged in!"
        }, 200
    
    data = request.get_json()
    # Check if data is None, which means the client did not send a JSON body or sent an invalid JSON.
    if not data:
        return {"error": "Missing JSON request"}, 400
    
    email = data.get('email', '').strip()
    raw_password = data.get('password', '')

    user = db.session.query(User).filter_by(email=email).first()

    if not user or not check_password_hash(user.password, raw_password):
        return {"error": "Invalid email or password"}, 401
    else:
        login_user(user, remember=True)
        return {
            "status": "success",
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }, 200
    
@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return {
        "status": "success",
        "message": "Logout successful"
    }, 200

@auth.route('/profile', methods=['GET'])
@login_required
def profile():
    # New Fetch method
    user = db.session.get(User, current_user.id)
    # Add The Path Of The Profile Picture To The Response
    image_url = url_for('static', filename='profile_pics/' + user.profile_pic, _external=True)

    user_data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "gender": user.gender,
        "profile_pic": image_url
    }

    if user.role == 'teacher':
        user_data['course_count'] = len(user.courses)
        user_data['my_courses'] = [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": course.price,
                "duration_hours": course.duration_hours,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + (course.thumbnail or 'default_course.jpg'), _external=True)
            }
            for course in user.courses
        ]
    else:
        user_data['enrollment_count'] = len(user.enrollments)
        user_data['enrolled_courses_list'] = [
            {
                "id": enrollment.enrolled_course.id,
                "title": enrollment.enrolled_course.title,
                "description": enrollment.enrolled_course.description,
                "price": enrollment.enrolled_course.price,
                "duration_hours": enrollment.enrolled_course.duration_hours,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + (enrollment.enrolled_course.thumbnail or 'default_course.jpg'), _external=True)
            }
            for enrollment in user.enrollments
        ]

    return {
        "status": "success",
        "data": user_data
    }, 200


@auth.route('/delete_account', methods=['DELETE'])
@login_required
def delete_account():
    # user = current_user
    # Fetch a fresh, session-attached user instance instead of using 'current_user' directly.
    # This prevents 'DetachedInstanceError' and ensures the object is bound to the current DB session.
    user = User.query.get(current_user.id) 

    try:
        # 1. Mark user for deletion in the session (Drafting).
        db.session.delete(user)
        # 2. Logout first to clear session cookies while the user object still exists in memory.
        logout_user()
        # 3. Commit to finalize the deletion of the user and all cascaded data in Postgres.
        db.session.commit()
        return {
            "status": "success",
            "message": "Account deleted successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not delete account. Database error."}, 500

    

    
   
    

    
    



