import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/generate"

# Еталонні дані для перевірки (що питаємо -> що очікуємо побачити)
EVAL_CASES = [
    {
        "product_name": "Pringles",
        "category": "Їжа та напої",
        "expected_brands": ["люкс", "chipster's", "flint"]
    },
    {
        "product_name": "1C",
        "category": "Програми та сервіси",
        "expected_brands": ["bas", "дебет плюс", "bimp", "master"]
    }
]

def calculate_match_percentage(expected_list, actual_names_list):
    """Рахує % збігу: скільки очікуваних брендів ШІ реально згадав."""
    if not expected_list:
        return 0.0
        
    actual_text = " ".join(actual_names_list).lower()
    matches = 0
    
    for expected in expected_list:
        if expected.lower() in actual_text:
            matches += 1
            
    return (matches / len(expected_list)) * 100

def run_evals():
    print("🚀 Починаємо Eval-тестування ШІ...\n")
    total_score = 0
    
    for idx, test_case in enumerate(EVAL_CASES, 1):
        product = test_case["product_name"]
        print(f"Тест {idx}: Аналіз для '{product}'")
        
        try:
            response = requests.post(API_URL, json={
                "product_name": product,
                "category": test_case["category"]
            })
            response.raise_for_status()
            
            data = response.json()
            
            # Парсимо JSON, який повернув ШІ
            ai_output = json.loads(data["data"]["description"])
            actual_brands = [item["name"] for item in ai_output.get("alternatives", [])]
            
            print(f"   Очікували (мінімум): {test_case['expected_brands']}")
            print(f"   ШІ згенерував:       {actual_brands}")
            
            # Рахуємо відсоток збігу
            match_percent = calculate_match_percentage(test_case["expected_brands"], actual_brands)
            total_score += match_percent
            
            print(f"   📊 Відсоток збігу: {match_percent:.1f}%\n")
            
        except Exception as e:
            print(f"   ❌ Помилка під час тесту: {e}\n")
            
    avg_score = total_score / len(EVAL_CASES)
    print(f"🏁 Загальний бал ШІ (Average Match): {avg_score:.1f}%")

if __name__ == "__main__":
    # Щоб тест пройшов, твій сервер (uvicorn) має бути запущений в іншому терміналі!
    run_evals()