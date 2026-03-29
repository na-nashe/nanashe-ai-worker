from fastapi import FastAPI
from dotenv import load_dotenv

# Завантажуємо .env ПЕРЕД імпортом сервісів
load_dotenv()

# Імпортуємо наш відокремлений сервіс
from ai_service import router as ai_router

app = FastAPI()

# Підключаємо роутер до головного додатку
app.include_router(ai_router)

@app.get("/")
def root():
    return {"message": "Server is running! Go to /docs to test."}