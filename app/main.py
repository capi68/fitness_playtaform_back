from fastapi import FastAPI
from .routers import trainers, clients, workout_plans, auth, templates, workout_sessions, exercise_logs, exercises

app = FastAPI(title="Fitness Platform API")

app.include_router(trainers.router)
app.include_router(clients.router)
app.include_router(workout_plans.router)
app.include_router(auth.router)
app.include_router(templates.router)
app.include_router(workout_sessions.router)
app.include_router(exercise_logs.router)
app.include_router(exercises.router)

@app.get("/")
def read_root():
    return {"message": "Fitness Platform API is running"}