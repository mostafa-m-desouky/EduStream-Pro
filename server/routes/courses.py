from models import User, Course, db
from flask import (Blueprint, request, url_for, jsonify)
from flask_login import login_required, current_user
from utils import media_handlers

courses = Blueprint('courses', __name__)

@courses.route('/all', methods=['GET'])
def get_all_courses():
    try:
        courses = Course.query.all()
        course_list = []
        for course in courses:
            course_list.append({
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": course.price,
                "duration_hours": course.duration_hours,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + (course.thumbnail or 'default_course.jpg'), _external=True),
                "author_name": course.author.username
            })
        return jsonify({"courses": course_list}), 200
    except Exception as e:
        return jsonify({"error": "Could not fetch courses. Database error."}), 500

@courses.route('/my_courses', methods=['GET'])
@login_required
def get_my_courses():
    try:
        my_courses_query = Course.query.filter_by(author_id=current_user.id).all()
        my_courses = []
        for course in my_courses_query:
            my_courses.append({
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": course.price,
                "duration_hours": course.duration_hours,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + (course.thumbnail or 'default_course.jpg'), _external=True)
            })
        return jsonify({"my_courses": my_courses}), 200
    except Exception as e:
        return jsonify({"error": "Could not fetch your course. Database error."}), 500

    
@courses.route('/get_course_details/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    try:
        course = db.session.get(Course, course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        lessons_list = []
        for lesson in course.lessons:
            lessons_list.append({
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "content_url": lesson.content_url,
                "order": lesson.order
            })

        return jsonify({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "duration_hours": course.duration_hours,
            "thumbnail_url": url_for('static', filename='course_thumbnails/' + (course.thumbnail or 'default_course.jpg'), _external=True),
            "author_name": course.author.username,
            "lessons": lessons_list
        }), 200
    except Exception as e:
        return jsonify({"error": "Could not fetch course details. Database error."}), 500


@courses.route('/create_course', methods=['POST'])
@login_required
def create_course():
    user = db.session.get(User, current_user.id)
    if current_user.role != 'teacher':
        return jsonify({"error": "Only teachers can create courses"}), 403

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price_raw = request.form.get('price', '0').strip()
    duration_raw = request.form.get('duration_hours', '0').strip()

    if not title or title == "":
        return jsonify({"error": "Title cannot be empty"}), 400

    if not price_raw or not duration_raw:
        return jsonify({"error": "Price and duration are required"}), 400
    
    try:
        price = float(price_raw)
        duration_hours = int(duration_raw)
    except ValueError:
        return jsonify({"error": "Price must be a number and duration must be an integer"}), 400
    
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
        return jsonify({
            "status": "success",
            "message": "Course created successfully",
            "course": {
                "id": new_course.id,
                "title": new_course.title,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + new_course.thumbnail, _external=True)
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not create course. Database error."}), 500

    
@courses.route('/update_course/<int:course_id>', methods=['PATCH'])
@login_required
def update_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if course.author_id != current_user.id:
        return jsonify({"error": "You can only update your own courses"}), 403
    
    new_title = request.form.get('title', '').strip()
    new_description = request.form.get('description', '').strip()
    price_raw = request.form.get('price', str(course.price))
    duration_raw = request.form.get('duration_hours', str(course.duration_hours))

    #[NOTE] For course updates, we allow partial updates. If a field is not provided, we keep the existing value.
    if new_title:
        course.title = new_title

    # [NOTE] For course updates, we allow partial updates. If a field is not provided, we keep the existing value.
    if new_description: 
        course.description = new_description

    if price_raw is not None and price_raw.strip() != "":
        try:
            course.price = float(price_raw.strip())
        except ValueError:
            return jsonify({"error": "Price must be a number"}), 400
        
    if duration_raw is not None and duration_raw.strip() != "":
        try:
            course.duration_hours = int(duration_raw.strip())
        except ValueError:
            return jsonify({"error": "Duration must be an integer"}), 400
        
    if 'course_pic' in request.files and request.files['course_pic'].filename != '':
        media_handlers.delete_old_picture(course.thumbnail, folder='course_thumbnails')

        course_pic = media_handlers.save_picture(request.files['course_pic'], folder='course_thumbnails')
        course.thumbnail = course_pic

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Course updated successfully",
            "updated_course": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "thumbnail_url": url_for('static', filename='course_thumbnails/' + course.thumbnail, _external=True)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not update course. Database error."}), 500

@courses.route('/delete_course/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if course.author_id != current_user.id:
        return jsonify({"error": "You can only delete your own courses"}), 403
    
    try:
        media_handlers.delete_old_picture(course.thumbnail, folder='course_thumbnails')

        db.session.delete(course)
        db.session.commit()
        return jsonify({"status": "success", "message": "Course deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not delete course. Database error."}), 500