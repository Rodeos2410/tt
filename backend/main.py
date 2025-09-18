from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .db import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    # Инициализация базы данных при старте
    init_db()


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Маркетплейса!"}
