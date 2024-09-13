import models
from db import engine
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, generate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],  # Adjust this to your needs (e.g., ["GET", "POST"])
    allow_headers=["*"],  # Adjust this to your needs (e.g., ["Content-Type", "Authorization"])
)

app.include_router(auth.router)
app.include_router(generate.router)

@app.get("/")
async def root():
    return {"message": "Hello from Try0n API!"}
