from models import User, Course, db
from flask import (Blueprint, request, url_for)
from flask_login import login_required, current_user
from utils import media_handlers

courses = Blueprint('courses', __name__)



@courses.route('/create_course', methods=['POST'])
@login_required
def create_course():
    user = db.session.get(User, current_user.id)
    if current_user.role != 'teacher':
        return {"error": "Only teachers can create courses"}, 403
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price_raw = request.form.get('price', '0').strip()
    duration_raw = request.form.get('duration_hours', '0').strip()

    if not title or not price_raw or not duration_raw:
        return {"error": "Title, price, and duration are required"}, 400
    
    try:
        price = float(price_raw)
        duration_hours = int(duration_raw)
    except ValueError:
        return {"error": "Price must be a number and duration must be an integer"}, 400
    
    if 'course_pic' in request.files and request.files['course_pic'].filename != '':
        course_pic = media_handlers.save_picture(request.files['course_pic'], folder='course_thumbnails')
    else:
        course_pic = 'default_course.jpg'
    

    new_course = Course(
        title=title,
        description=description,
        price=price,
        duration_hours=duration_hours,
        thumbnail=course_pic,
        author_id=current_user.id
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return {
            "status": "success",
            "message": "Course created successfully",
            "course": {
                "id": new_course.id,
                "title": new_course.title,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + new_course.thumbnail, _external=True)
            }
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not create course. Database error."}, 500

    
@courses.route('/update_course/<int:course_id>', methods=['PATCH'])
@login_required
def update_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return {"error": "Course not found"}, 404
    
    if course.author_id != current_user.id:
        return {"error": "You can only update your own courses"}, 403
    
    title = request.form.get('title', course.title).strip()
    description = request.form.get('description', course.description).strip()
    price_raw = request.form.get('price', str(course.price))
    duration_raw = request.form.get('duration_hours', str(course.duration_hours))

    if price_raw is not None and price_raw.strip() != "":
        try:
            course.price = float(price_raw.strip())
        except ValueError:
            return {"error": "Price must be a number"}, 400
        
    if duration_raw is not None and duration_raw.strip() != "":
        try:
            course.duration_hours = int(duration_raw.strip())
        except ValueError:
            return {"error": "Duration must be an integer"}, 400
        
    if 'course_pic' in request.files and request.files['course_pic'].filename != '':
        media_handlers.delete_old_picture(course.thumbnail, folder='course_thumbnails')

        course_pic = media_handlers.save_picture(request.files['course_pic'], folder='course_thumbnails')
        course.thumbnail = course_pic

    course.title = title
    course.description = description

    try:
        db.session.commit()
        return {
            "status": "success",
            "message": "Course updated successfully",
            "updated_course": {
                "id": course.id,
                "title": course.title,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + course.thumbnail, _external=True)
            }
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not update course. Database error."}, 500