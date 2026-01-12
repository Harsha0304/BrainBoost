---

# 🧠 BrainBoost

### A Gamified E-Learning Platform

BrainBoost is a **Django-based gamified e-learning platform** designed to improve learner engagement and motivation by integrating **game mechanics** such as points, badges, levels, quizzes, and progress tracking into online education.
This project is developed as a **final-year academic project at NTTF**.

---

## 📌 Project Objectives

* Provide an interactive online learning platform
* Increase learner motivation using gamification techniques
* Track user progress, scores, and achievements
* Enable instructors/admins to manage courses and content
* Offer a scalable backend architecture using Django

---

## ✨ Key Features

* User authentication (Student / Admin)
* Course and lesson management
* Enrollment and progress tracking
* Gamification system (points, badges, levels)
* Interactive quizzes with instant feedback
* Admin dashboard using Django Admin
* REST API support (future frontend integration)

---

## 🛠️ Technology Stack

| Layer           | Technology                    |
| --------------- | ----------------------------- |
| Backend         | Django, Django REST Framework |
| Database        | SQLite (development)          |
| Frontend        | Planned (React / Flutter)     |
| Auth            | Django Authentication         |
| Version Control | Git & GitHub                  |

---

## 🗂️ Project Structure

```
brainboost/
│
├── brainboost_core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
├── courses/
├── gamification/
├── quizzes/
│
├── manage.py
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* pip
* Virtual Environment (venv)

---

### Installation Steps

```bash
# Clone the repository
git clone <your-repo-url>
cd brainboost

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install django djangorestframework

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Open browser:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)
👉 Admin panel: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 📊 Future Enhancements

* Leaderboards and challenges
* AI-based personalized learning recommendations
* Mobile/Web frontend integration
* Push notifications and reminders
* Analytics dashboard for learners

---

## 🎓 Academic Note

This project is developed **strictly for academic purposes** as part of the **NTTF final-year curriculum** and is not intended for commercial use.

---

## 👤 Author

**Harsha Seshadri**
Final Year Student, NTTF

---

## 📄 License

This project is intended for **educational use only**.

---

If you want, next I can:

* Add a **Professional `.gitignore` for Django**
* Create **requirements.txt**
* Help you write **commit messages**
* Start **Step-7: Custom User Model**

Just say **next** 🚀
