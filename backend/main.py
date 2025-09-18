from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from db import init_db

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
#    pass


@app.post("/")
def read_root():
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS limpopo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
    ''')
    return {"message": "Ты создал таблицу limpopo!"}

