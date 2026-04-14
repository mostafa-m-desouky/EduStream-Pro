from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import db, Course, Enrollment, Payment
from datetime import datetime

enrollments = Blueprint('enrollments', __name__)

@enrollments.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_in_course(course_id):
    if current_user.role == 'teacher':
        return jsonify({"error": "Unauthorized. Teachers cannot enroll in courses."}), 403
    else:
        course = db.session.get(Course, course_id)
        if not course:
            return jsonify({"error": "The requested course was not found."}), 404
        
        existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        
        if existing_enrollment:
            if existing_enrollment.status == 'active':
                return jsonify({"error": "You are already enrolled and have access to this course."}), 400
            elif existing_enrollment.status == 'pending':
                return jsonify({
                "message": "You have a pending enrollment. Please complete your payment.",
                "payment_url": f"/payments/checkout/{course_id}"
            }), 200
        
        try:
            initial_status = 'active' if course.price == 0 else 'pending'

            new_enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course_id,
                enrolled_at=datetime.utcnow(),
                status=initial_status
            )
            db.session.add(new_enrollment)
            db.session.flush() 

            if course.price > 0:
                new_payment = Payment(
                    transaction_id=f"TXN-{current_user.id}-{course_id}-{int(datetime.utcnow().timestamp())}",
                    amount=course.price,
                    status='pending',
                    payment_method='waiting',
                    user_id=current_user.id,
                    course_id=course_id,
                    enrollment_id=new_enrollment.id
                )
                db.session.add(new_payment)

            db.session.commit()
            response_data = {
                "status": initial_status,
                "message": f"Successfully registered for {course.title}.",
                "course_id": course_id
            }

            if initial_status == 'pending':
                response_data["action_required"] = "Proceed to payment to unlock course content."
                response_data["checkout_url"] = f"/payments/checkout/{course_id}"

            return jsonify(response_data), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Internal server error. Please try again later."}), 500