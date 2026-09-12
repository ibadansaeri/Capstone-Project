from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Integer, Column, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ----- Database Model -----
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_done = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


# ----- Pydantic Model -----
class Task(BaseModel):
    id: int
    title: str
    is_done: bool = False


# ----- CREATE (POST) -----
@app.post("/tasks")
def creat_task(task: Task):
    db = SessionLocal()
    new_task = TaskDB(id=task.id, title=task.title, is_done=task.is_done)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    return new_task


# ----- READ (GET) -----
@app.get("/tasks")
def get_task():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return tasks


# ----- UPDATE (PUT) -----
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    db = SessionLocal()

    existing_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not existing_task:
        db.close()
        return {"message": "Task not found"}

    existing_task.title = task.title
    existing_task.is_done = task.is_done

    db.commit()
    db.refresh(existing_task)
    db.close()

    return existing_task


# ----- DELETE -----
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()

    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not task:
        db.close()
        return {"message": "Task not found"}

    db.delete(task)
    db.commit()
    db.close()

    return {"message": "Task deleted successfully"}