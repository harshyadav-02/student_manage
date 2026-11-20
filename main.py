from typing import Optional
import psycopg
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from database import get_connection

app = FastAPI(title="Student Manage API")


@app.exception_handler(psycopg.Error)
def database_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Database error, try again later"})


class StudentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=3, le=25)
    class_name: str = Field(min_length=1, max_length=20)


class StudentPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, ge=3, le=25)
    class_name: Optional[str] = Field(default=None, min_length=1, max_length=20)


class StudentOut(StudentCreate):
    id: int


def check_found(row):
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row


@app.post("/students", status_code=201, response_model=StudentOut)
def create_student(student: StudentCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO students (name, age, class_name) "
                "VALUES (%s, %s, %s) RETURNING *",
                (student.name, student.age, student.class_name),
            )
            return cur.fetchone()


@app.get("/students", response_model=list[StudentOut])
def get_students(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM students ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return cur.fetchall()


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int = Path(gt=0)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()
    return check_found(row)


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student: StudentCreate, student_id: int = Path(gt=0)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE students SET name = %s, age = %s, class_name = %s "
                "WHERE id = %s RETURNING *",
                (student.name, student.age, student.class_name, student_id),
            )
            row = cur.fetchone()
    return check_found(row)


@app.patch("/students/{student_id}", response_model=StudentOut)
def patch_student(student: StudentPatch, student_id: int = Path(gt=0)):
    if not student.model_dump(exclude_none=True):
        raise HTTPException(status_code=400, detail="Update ke liye kam se kam ek field bhejo")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE students SET "
                "name = COALESCE(%s, name), "
                "age = COALESCE(%s, age), "
                "class_name = COALESCE(%s, class_name) "
                "WHERE id = %s RETURNING *",
                (student.name, student.age, student.class_name, student_id),
            )
            row = cur.fetchone()
    return check_found(row)


@app.delete("/students/{student_id}")
def delete_student(student_id: int = Path(gt=0)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id = %s RETURNING id", (student_id,))
            row = cur.fetchone()
    check_found(row)
    return {"message": "Student deleted"}