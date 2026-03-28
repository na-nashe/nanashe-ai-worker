# Беремо легку версію Python
FROM python:3.11-slim

# Вказуємо робочу папку
WORKDIR /app

# Копіюємо список бібліотек
COPY requirements.txt .

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь наш код
COPY . .

# Відкриваємо порт
EXPOSE 8000

# Команда для запуску сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]