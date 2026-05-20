import csv
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from ai_service import router as ai_router
from cashback_storage import CASHBACK_ITEMS

app = FastAPI()

def load_cashback_database():
    file_path = 'national_cashback.csv'
    
    if not os.path.exists(file_path):
        print(f"⚠️ Файл {file_path} не знайдено!")
        return

    try:
        with open(file_path, mode='r', encoding='cp1251') as file:
            for line in file:
                clean_line = line.strip().lower()
                if clean_line:
                    CASHBACK_ITEMS.add(clean_line)
        print(f"🎒 Базу Нацкешбеку успішно завантажено в RAM! Кількість позицій: {len(CASHBACK_ITEMS)}")
    except Exception as e:
        print(f"❌ Помилка під час читання файлу кешбеку: {e}")

@app.on_event("startup")
def on_startup():
    load_cashback_database()

app.include_router(ai_router)

@app.get("/")
def root():
    return {"message": "Server is running! Go to /docs to test."}