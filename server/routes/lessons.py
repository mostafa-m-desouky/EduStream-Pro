from flask import Blueprint, request, url_for
from flask_login import login_required, current_user
from models import db, Lesson, Course

lessons = Blueprint('lessons', __name__)

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