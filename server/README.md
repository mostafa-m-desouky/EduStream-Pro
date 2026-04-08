# 🖥️ EduTech - Backend API (Server)

This is the core engine of the EduTech platform, built using **Python** and **Flask**. It handles data persistence, authentication, and the business logic for the entire application.

![Project Architecture](./architecture_image.png)

## 🛠️ Technical Stack

- **Framework:** Flask
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Migrations:** Flask-Migrate
- **Authentication:** Flask-Login (UserMixin implemented)
- **Security:** Werkzeug (Password Hashing)

---

## ✨ Key Features (Advanced)

- **Course Enrollment System:** A robust system to manage student subscriptions to courses using a Many-to-Many relationship logic.
- **Payment Processing:** Dedicated tracking for financial transactions including:
  - Transaction IDs and status tracking (Pending, Succeeded, Failed).
  - Support for multiple payment methods (Vodafone Cash, Credit Card, Fawry, Promo Codes).
- **Relational Integrity:** - **Cascade Deletes:** If a user or course is deleted, all related enrollments and payments are handled safely.
  - **Backrefs:** Seamless data navigation between Students, Courses, and Payments.
- **Role-Based Access:** Automatic validation of user roles (Admin, Instructor, Student).

---

## 🏗️ Database Schema & Relationships

The server manages five main entities:

1. **Users:** Handles profiles and serves as the 'Payer' and 'Student'.
2. **Courses:** Created by Instructors, containing multiple lessons.
3. **Lessons:** Organized content within courses.
4. **Enrollments:** Connects Users to Courses with timestamps.
5. **Payments:** Records every financial transaction linked to a specific User.

---

## Server Installation

1. Navigate to the server directory:
   cd server

2. Setup Virtual Environment:
   python -m venv venv

3. Activate Virtual Environment:
   Windows:

   ```bash
      npm run test
   ```

   Mac/Linux:

   ```bash
   source venv/bin/activate
   ```

4. Install Dependencies:
   pip install -r requirements.txt

## Database Configuration

1. Open app.py and locate SQLALCHEMY_DATABASE_URI.
2. Update the URI with your local PostgreSQL credentials:
   postgresql://username:password@localhost:5432/database_name
3. Run migrations to create tables:
   flask db upgrade

## Run The Application

1. Ensure your virtual environment is active.
2. Start the Flask server:
   flask run
3. The server will be available at: http://127.0.0.1:5000

## API Documentation

### Authentication Routes:

- Register User: POST /api/auth/register
- Login User: POST /api/auth/login

### Course Management:

- Create Course: POST /api/courses/create_course (Instructors Only)
- Update Course: PATCH /api/courses/update_course/<id> (Author Only)
- Delete Course: DELETE /api/courses/delete_course/<id> (Author Only)

### Payments & Enrollments:

- Process Payment: POST /api/payments/checkout
- Enroll in Course: POST /api/enrollments/join
- My Enrolled Courses: GET /api/enrollments/my-courses

## Project Architecture

- Models: Includes User, Course, Lesson, Payment, and Enrollment tables.
- Relationships: Implements One-to-Many and Many-to-Many logic.
- Integrity: Supports Cascade Deletes for all related records.
