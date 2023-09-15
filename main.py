# backend/main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from peewee import Model, CharField, IntegerField, PostgresqlDatabase
from playhouse.db_url import connect
from pydantic import ValidationError

# Define the ElephantSQL PostgreSQL database connection
DATABASE_URL = "postgres://sfwocxbz:9-egT1nKDFM_O7EzLc6bI-l-Hoso87MQ@snuffleupagus.db.elephantsql.com/sfwocxbz"

# Initialize FastAPI app
app = FastAPI()

# CORS Configuration
origins = ["https://next-frontend-umber.vercel.app/"]  # Update with the actual URL of your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Define a Peewee model for the Student table
db = connect(DATABASE_URL)

class StudentModel(Model):
    name = CharField()
    age = IntegerField()
    year = CharField()

    class Meta:
        database = db

# Create tables if they don't exist
with db:
    db.create_tables([StudentModel], safe=True)

# Pydantic models
class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    year: Optional[str] = None

class Student(BaseModel):
    name: str
    age: int
    year: str

# Dependency to get the database connection
def get_db():
    with db:
        yield db

# CRUD operations

@app.get("/")
def main():
    return {"Message": "Hello Vishal!"}

@app.post("/create-student/")
async def create_student(student: Student, db: PostgresqlDatabase = Depends(get_db)):
    try:
        print("Received student data:", student)  # Add this line for debugging
        student_model = StudentModel.create(name=student.name, age=student.age, year=student.year)
        return {"name": student_model.name, "age": student_model.age, "year": student_model.year}
    except ValidationError as e:
        # FastAPI will raise a ValidationError when the request data doesn't match the Pydantic model
        # Return a 400 Bad Request response with the validation error details
        return {"detail": e.errors(), "error_type": "validation_error"}
    except Exception as e:
        print("Error creating student:", e)  # Print the error for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")
