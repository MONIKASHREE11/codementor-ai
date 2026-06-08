# 🧠 CodeMentor AI — Personalized Programming Tutor Agent

A full-stack AI application that acts as a personalized coding tutor. It analyzes student code, remembers mistakes across sessions, and adapts its feedback based on each learner's history — built to demonstrate real-world skills in LLM integration, backend API design, and database-driven memory systems.

---

## 💡 Why I Built This

Most AI tools give the same generic response to everyone. I wanted to build something that actually remembers who you are — tracking your weak topics, repeated mistakes, and progress over time — and adjusts its feedback accordingly. This project demonstrates agentic AI behavior with persistent memory, not just a simple chatbot.

---

## 🚀 Features

- **Personalized Feedback** — AI explains errors based on your skill level and history
- **Persistent Memory** — Tracks mistakes and progress across multiple sessions
- **Learner Profiling** — Builds a profile of weak topics, strong topics, and misconceptions
- **Multi-language Support** — Python, JavaScript, Java, C++
- **Adaptive Explanations** — Adjusts explanation style based on experience level
- **REST API Backend** — Clean FastAPI endpoints for student registration and code analysis

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | SQLAlchemy + SQLite |
| LLM | LLaMA 3.3 70B (via Groq API) |
| Language | Python 3.11 |
| Version Control | Git + GitHub |

---

## 📁 Project Structure

codementor-ai/
├── backend/
│   ├── routes/
│   │   ├── student.py       # Student registration API endpoints
│   │   └── tutor.py         # Code analysis + LLM integration
│   ├── database.py          # SQLAlchemy database connection
│   ├── main.py              # FastAPI app entry point
│   ├── memory_manager.py    # Session memory and learner profile logic
│   └── models.py            # Database models (Student, Profile, Submissions)
├── frontend/
│   └── app.py               # Streamlit user interface
├── .gitignore
└── README.md

---

## ⚙️ Setup Instructions

1. Clone the repository
git clone https://github.com/MONIKASHREE11/codementor-ai.git
cd codementor-ai

2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install fastapi uvicorn sqlalchemy streamlit python-dotenv pydantic groq

4. Set up environment variables
Create a .env file in the root folder:
GROQ_API_KEY=your_groq_api_key_here

5. Run the backend
cd backend
uvicorn main:app --reload

6. Run the frontend in a new terminal
cd frontend
streamlit run app.py

7. Open in browser
http://localhost:8501

---

## 🎯 How It Works

1. Student registers with name and email
2. A learner profile is created and stored in the database
3. Student submits code with topic and language selected
4. Backend fetches the student's history and builds a personalized prompt
5. LLaMA 3.3 via Groq analyzes the code and returns tailored feedback
6. Session is saved and learner profile is updated for next time

---

## 🔑 Key Concepts Demonstrated

- LLM integration with real API calls
- Agentic behavior with memory across sessions
- REST API design with FastAPI
- Relational database modeling with SQLAlchemy
- Full stack Python application
- Clean project structure and version control

---

## 👩‍💻 About

Built by Monika Shree — MSc. Data Science Student at Christ University, Bangalore.
Actively building projects to develop real-world AI and software engineering skills.

