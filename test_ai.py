import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Завантажуємо твій секретний ключ з файлу .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Перевірка, щоб ми відразу знали, якщо щось не так
if not api_key:
    print("❌ Помилка: Ключ не знайдено! Перевір файл .env")
    exit()

# 2. Підключаємося до OpenAI
client = OpenAI(api_key=api_key)

print("Запит відправлено. Чекаємо на відповідь від ШІ... \n")

# 3. Робимо тестовий запит
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Швидка та економна модель
    messages=[
        {"role": "system", "content": "Ти експерт з українського програмного забезпечення. Давай чіткі та короткі відповіді."},
        {"role": "user", "content": "Назви одну найкращу українську альтернативу для російської бухгалтерської програми 1С."}
    ]
)

# 4. Друкуємо те, що відповів штучний інтелект
print(" Відповідь OpenAI:")
print(response.choices[0].message.content)