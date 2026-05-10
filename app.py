from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODELS =================
class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Event(BaseModel):
    id: int
    title: str
    date: str
    start_time: str
    end_time: str
    user_id: int
    status: str = "pending"   # 🔥 DEFAULT STATUS

# ================= TEMP DB =================
users: List[User] = [
    User(id=1, name="Admin", email="admin@gmail.com", password="1234", role="admin"),
    User(id=2, name="User", email="user@gmail.com", password="1234", role="user")
]

events: List[Event] = []

# ================= AUTH =================
@app.post("/register")
def register(user: User):
    for u in users:
        if u.email == user.email:
            raise HTTPException(status_code=400, detail="Email exists")

    users.append(user)
    return {"message": "Registered"}

@app.post("/login")
def login(req: LoginRequest):
    for u in users:
        if u.email == req.email and u.password == req.password:
            return {"user": u}

    raise HTTPException(status_code=401, detail="Invalid credentials")

# ================= USERS =================
@app.get("/users")
def get_users():
    return users

# ================= EVENTS =================

# GET EVENTS (with user name)
@app.get("/events")
def get_events():
    result = []

    for e in events:
        user_name = "Unknown"

        for u in users:
            if u.id == e.user_id:
                user_name = u.name

        result.append({
            "id": e.id,
            "title": e.title,
            "date": e.date,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "status": e.status,
            "user_id": e.user_id,
            "user_name": user_name
        })

    return result

# CREATE EVENT
@app.post("/create-event")
def create_event(event: Event):
    event.status = "pending"   # 🔥 FORCE DEFAULT
    events.append(event)
    return {"message": "Event created"}

# DELETE EVENT
@app.delete("/delete-event/{id}")
def delete_event(id: int):
    global events
    events = [e for e in events if e.id != id]
    return {"message": "Deleted"}

# REQUEST CANCEL
@app.put("/request-cancel/{id}")
def request_cancel(id: int):
    for e in events:
        if e.id == id:
            e.status = "pending_cancel"
            return {"message": "Cancel requested"}

    raise HTTPException(status_code=404, detail="Event not found")

# APPROVE EVENT
@app.put("/approve/{id}")
def approve_event(id: int):
    for e in events:
        if e.id == id:
            e.status = "scheduled"
            return {"message": "Approved"}

    raise HTTPException(status_code=404, detail="Event not found")

# REJECT EVENT
@app.put("/reject/{id}")
def reject_event(id: int):
    for e in events:
        if e.id == id:
            e.status = "cancelled"
            return {"message": "Rejected"}

    raise HTTPException(status_code=404, detail="Event not found")

# APPROVE CANCEL REQUEST
@app.put("/approve-cancel/{id}")
def approve_cancel(id: int):
    for e in events:
        if e.id == id:
            e.status = "cancelled"
            return {"message": "Cancel approved"}

    raise HTTPException(status_code=404, detail="Event not found")

# REJECT CANCEL REQUEST
@app.put("/reject-cancel/{id}")
def reject_cancel(id: int):
    for e in events:
        if e.id == id:
            e.status = "scheduled"
            return {"message": "Cancel rejected"}

    raise HTTPException(status_code=404, detail="Event not found")

# RESCHEDULE EVENT
@app.put("/reschedule/{id}")
def reschedule_event(id: int, data: dict):
    for e in events:
        if e.id == id:
            e.date = data.get("date", e.date)
            e.start_time = data.get("start_time", e.start_time)
            e.end_time = data.get("end_time", e.end_time)
            return {"message": "Rescheduled", "event": e}

    raise HTTPException(status_code=404, detail="Event not found")