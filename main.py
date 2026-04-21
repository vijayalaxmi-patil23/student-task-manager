import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()
def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to DB
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    status TEXT
)
""")
conn.commit()


# Model
class Task(BaseModel):
    title: str
    status: str = "pending"


# Create Task
@app.post("/tasks")
def add_task(task: Task):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, status) VALUES (?, ?)",
        (task.title, task.status)
    )

    conn.commit()
    conn.close()

    return {"message": "Task added"}


# Get All Tasks
@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    return [
        {"id": row["id"], "title": row["title"], "status": row["status"]}
        for row in rows
    ]


# Update Task
@app.put("/tasks/{task_id}")
def update_task(task_id: int):
    cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    return {"message": "Task updated"}


# Delete Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    return {"message": "Task deleted"}
