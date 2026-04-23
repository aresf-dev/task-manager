from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
from auth import hash_password, verify_password, create_access_token, get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# --- Auth routes ---

@app.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    db_user = models.User(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- Task routes (now protected) ---

@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Task).all()

@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}