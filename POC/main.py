import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# SQLAlchemy setup: define the database connection URL.
# Use the host IP obtained earlier for the Windows host.
DATABASE_URL = "postgresql://chatbot_user:postgres@172.18.158.140:5432/chatbotdb"

# Create engine and session.
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debug SQL logs
SessionLocal = sessionmaker(bind=engine)

# Base class for declarative models
Base = declarative_base()

# Define the User model (maps to the users table)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

# Define the QuestionAnswer model (maps to the questions_answers table)
class QuestionAnswer(Base):
    __tablename__ = "questions_answers"
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

# (Optional) Create tables in the database if they don't exist yet.
# In a real app, you might handle migrations separately, but for dev:
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")

# Initialize FastAPI app
app = FastAPI()

# Pydantic models for request bodies
class LoginRequest(BaseModel):
    email: str
    password: str

class QuestionRequest(BaseModel):
    question: str

@app.post("/login")
def login(req: LoginRequest):
    """Authenticate user by email and password (plaintext match)."""
    session = SessionLocal()
    try:
        # Query the database for a user with matching email and password
        user = session.query(User).filter_by(email=req.email, password=req.password).first()
        if user:
            return {"status": "success", "role": user.role, "email": user.email}
        else:
            # Unauthorized if no match
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        # Log the error (in real scenario) and return a generic server error
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        session.close()

@app.post("/ask")
def ask_question(req: QuestionRequest):
    """Return an answer to the question if it exists in the database."""
    session = SessionLocal()
    try:
        # Perform case-insensitive lookup by comparing lowercased question text
        query_text = req.question.strip().lower()
        qa = session.query(QuestionAnswer).filter(QuestionAnswer.question == query_text).first()
        if qa:
            return {"answer": qa.answer}
        else:
            raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        session.close()
