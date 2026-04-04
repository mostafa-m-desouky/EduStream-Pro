from flask import (Blueprint, request)
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from utils import media_handlers


auth = Blueprint('auth', __name__)

ALLOWED_ROLES = ['student', 'teacher']

@auth.route('/register', methods=['POST'])
def register():
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


    

    
   
    

    
    



