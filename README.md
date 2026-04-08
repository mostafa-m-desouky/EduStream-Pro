# 🎓 EduTech Platform - Full Stack Project

This is a comprehensive E-learning platform project consisting of a Backend API and a Frontend Client.

## 📂 Project Structure

The project is divided into two main directories:

1. **Server (Backend):**
   - Built with: **Python & Flask**.
   - Database: **PostgreSQL** with SQLAlchemy ORM.
   - Responsibilities: Authentication, Database management, and Business logic.

2. **Client (Frontend):**
   - Responsibilities: User Interface and consuming the Backend API.

---

## 🚀 Getting Started

To run the full project, follow the instructions inside each directory.

### 🔧 Server Setup (Backend)

1. Navigate to the server folder: `cd server`
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Configure your Database URI in `app.py`.
6. Run the server: `flask run`

### 💻 Client Setup (Frontend)

1. Navigate to the client folder: `cd client`
2. Follow the specific setup instructions for the frontend framework used.

---

## 🛠️ Tech Stack (Overview)

- **Backend:** Flask, PostgreSQL, SQLAlchemy, Flask-Migrate.
- **Authentication:** Flask-Login with secure password hashing.
- **Architecture:** RESTful API design.

---

## 🔗 Main API Endpoints (Server)

- **Auth:** `POST /api/auth/register`, `POST /api/auth/login`
- **Courses:** `POST /api/courses/create_course`, `PATCH /api/courses/course_update/<id>`, `DELETE /api/courses/delete_course/<id>`

---

## 📝 Project Notes

- The project follows a "Client-Server" architecture.
- The Backend handles all security and data persistence.
- The Frontend focuses on the user experience and interaction.
