from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import load_db, list_questions, generate_template
from judge import Judge
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  
import os
import uuid

app = FastAPI()
db = load_db()
runner = Judge(db)

origins = [  
    "http://localhost:5173",   
    "http://localhost:8000", 
]
app.add_middleware(  
    CORSMiddleware,  
    allow_origins=origins, # Allows specific origins  
    allow_credentials=True,  
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)  
    allow_headers=["*"], # Allows all headers  
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure folder exists
UPLOAD_DIR = "questions"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# GET /api/questions → list all questions
@app.get("/api/questions")
def get_questions():
    result = []
    for qid, data in db.items():
        result.append({
            "id": qid,
            "title": data["title"],
            "difficulty": data["difficulty"]
        })
    return result

# POST /api/questions/generate → generate template
class GenerateInput(BaseModel):
    question_id: str

@app.post("/api/questions/generate")
def generate(input: GenerateInput):
    generate_template(db, input.question_id)
    return {"status": "template generated"}

class RunCodeRequest(BaseModel):
    question_id: str
    code: str

@app.post("/api/questions/run")
async def run_code(input: RunCodeRequest):
    runner = Judge(db)  # your database object
    # Pass the code string directly to Judge
    result = runner.run(input.question_id, user_code_str=input.code)
    return result

@app.get("/api/questions/{question_id}")  
def get_question_details(question_id: str):  
    # 'db' is the dictionary you loaded with load_db()  
    if question_id not in db:  
        # If the ID doesn't exist, raise a 404 error  
        raise HTTPException(status_code=404, detail="Question not found")  
      
    # Return the full data for the requested question  
    return db[question_id]  