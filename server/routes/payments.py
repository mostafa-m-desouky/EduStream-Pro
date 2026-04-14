from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Course, Enrollment, Payment
from datetime import datetime

payments = Blueprint('payments', __name__)

@payments.route('/checkout/<int:course_id>', methods=['GET'])
@login_required
def checkout(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Find the pending enrollment for this user and course
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, 
        course_id=course_id, 
        status='pending'
    ).first()

    if not enrollment:
        return jsonify({"error": "No pending enrollment found for this course"}), 400

    return jsonify({
        "course_title": course.title,
        "amount_to_pay": course.price,
        "currency": "EGP",
        "instructions": "Please choose a payment method: Vodafone Cash or Fawry"
    }), 200


@payments.route('/confirm/<int:course_id>', methods=['POST'])
@login_required
def confirm_payment(course_id):
    data = request.get_json()
    payment_method = data.get('payment_method')
    
    if not payment_method:
        return jsonify({"error": "Please provide a payment method"}), 400

    payment = Payment.query.filter_by(
        user_id=current_user.id, 
        course_id=course_id, 
        status='pending'
    ).first()

    if not payment:
        return jsonify({"error": "No pending payment found for this transaction"}), 404

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, 
        course_id=course_id, 
        status='pending'
    ).first()

    try:
        
        payment.status = 'succeeded'
        payment.payment_method = payment_method
        
        if enrollment:
            enrollment.status = 'active'
        
        db.session.commit()
        

        return jsonify({
            "status": "success",
            "message": "Payment confirmed! You now have full access to the course."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to confirm payment: {str(e)}"}), 500