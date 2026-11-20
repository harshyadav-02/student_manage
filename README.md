# Student Manage API

FastAPI + raw PostgreSQL (psycopg, no ORM) se bana Student CRUD project.

## Setup
1. `python -m venv venv` aur `venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `.env.example` ko copy karke `.env` banao aur apna password daalo
4. PostgreSQL mein `student_db` banao aur `students` table ki SQL chalao
5. `uvicorn main:app --reload`

## Endpoints
| Method | URL | Kaam |
|--------|-----|------|
| POST | /students | Naya student |
| GET | /students | Saare students (limit, offset) |
| GET | /students/{id} | Ek student |
| PUT | /students/{id} | Poora update |
| PATCH | /students/{id} | Thoda update |
| DELETE | /students/{id} | Delete |

Docs: http://127.0.0.1:8000/docs