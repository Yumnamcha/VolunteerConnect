from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal, run_light_migrations
from .seed import seed_demo

from .routers import auth, campaigns, applications, messages, dashboard

app = FastAPI(
    title="VolunteerConnect API",
    description="REST API for NGO volunteer and campaign coordination",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://volunteer-connect-ecru.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)
run_light_migrations()

with SessionLocal() as db:
    seed_demo(db)

app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(applications.router)
app.include_router(messages.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "message": "VolunteerConnect API is running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
