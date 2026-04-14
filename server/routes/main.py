from flask import Blueprint, jsonify
from models import Course

main = Blueprint('main', __name__)

@main.route('/')
def index():
    latest_courses = Course.query.order_by(Course.id.desc()).limit(6).all()
    
    courses_data = []
    for course in latest_courses:
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description[:100] + "...",
            "price": course.price,
            "thumbnail": course.thumbnail
        })

    return jsonify({
        "welcome_message": "Welcome to our E-Learning Platform",
        "featured_courses": courses_data,
        "statistics": {
            "total_students": 1500,
            "total_courses": len(latest_courses),
            "expert_instructors": 20
        }
    }), 200