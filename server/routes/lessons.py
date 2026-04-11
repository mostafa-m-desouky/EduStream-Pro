from flask import Blueprint, request, url_for
from flask_login import login_required, current_user
from models import db, Lesson, Course

lessons = Blueprint('lessons', __name__)

@lessons.route('/course/<int:course_id>/lessons', methods=['GET'])
def get_lessons(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return {"error": "Course not found"}, 404
    
    lessons_list = []
    for lesson in course.lessons:
        lessons_list.append({
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "content_url": lesson.content_url,
            "order": lesson.order
        })
    return {
        "course_title": course.title,
        "total_lessons": len(lessons_list),
        "lessons": lessons_list
    }, 200

@lessons.route('/lesson/<int:lesson_id>', methods=['GET'])
def get_lesson_details(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return {"error": "Lesson not found"}, 404
    
    prev_lesson = Lesson.query.filter_by(
        course_id=lesson.course_id, 
        order=lesson.order - 1
    ).first()

    next_lesson = Lesson.query.filter_by(
        course_id=lesson.course_id, 
        order=lesson.order + 1
    ).first()
    
    return {
        "status": "success",
        "data": {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "content_url": lesson.content_url,
            "order": lesson.order,
            "course_info": {
                "id": lesson.course_id,
                "title": lesson.course.title
            },
            "navigation": {
                "prev_lesson_id": prev_lesson.id if prev_lesson else None,
                "next_lesson_id": next_lesson.id if next_lesson else None
            }
        }
    }, 200

@lessons.route('/create_lesson/<int:course_id>', methods=['POST'])
@login_required
def create_lesson(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return {"error": "Course not found"}, 404
    if course.author_id != current_user.id:
        return {"error": "Unauthorized. Only the course author can add lessons."}, 403
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    # [NOTE] For production scalability, we store video content as URLs. 
    # Storing large video files directly on the application server can lead to 
    # storage exhaustion and high bandwidth costs. Using external URLs (e.g., YouTube, 
    # Vimeo, or Cloudinary) ensures faster streaming and better server performance.
    content_url = request.form.get('content_url', '').strip()
    current_lessons_count = Lesson.query.filter_by(course_id=course_id).count()
    new_order = current_lessons_count + 1

    if not title:
        return {"error": "Lesson title is required"}, 400
    if not content_url:
        return {"error": "Content URL is required"}, 400

    new_lesson = Lesson(
        title=title,
        description=description,
        content_url=content_url,
        order=new_order,
        course_id=course_id
    )
    try:
        db.session.add(new_lesson)
        db.session.commit()
        return {
            "message": "Lesson created successfully",
            "lesson": {
                "id": new_lesson.id,
                "title": new_lesson.title,
                "description": new_lesson.description,
                "content_url": new_lesson.content_url,
                "order": new_lesson.order
            }
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not create lesson. Database error."}, 500

@lessons.route('/update_lesson/<int:lesson_id>', methods=['PATCH'])
@login_required
def update_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return {"error": "Lesson not found"}, 404

    if lesson.course.author_id != current_user.id:
        return {"error": "You don't have permission to update this lesson"}, 403

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    content_url = request.form.get('content_url', '').strip()

    if title:
        lesson.title = title
    if description:
        lesson.description = description
    if content_url:
        lesson.content_url = content_url

    try:
        db.session.commit()
        return {
            "message": "Lesson updated successfully",
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "content_url": lesson.content_url,
                "order": lesson.order
            }
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Could not update lesson. Database error."}, 500

@lessons.route('/delete_lesson/<int:lesson_id>', methods=['DELETE'])
@login_required 
def delete_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    
    if not lesson:
        return {"error": "Lesson not found"}, 404

    if lesson.course.author_id != current_user.id:
        return {"error": "You don't have permission to delete this lesson"}, 403

    course_id = lesson.course_id
    deleted_order = lesson.order

    db.session.delete(lesson)

    subsequent_lessons = Lesson.query.filter(
        Lesson.course_id == course_id,
        Lesson.order > deleted_order
    ).all()

    for l in subsequent_lessons:
        l.order -= 1

    db.session.commit()

    return {
        "status": "success",
        "message": f"Lesson {lesson_id} deleted and subsequent lessons re-ordered."
    }, 200