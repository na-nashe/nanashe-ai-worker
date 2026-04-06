import json
from models import SearchRequest, AlternativesResponse

SYSTEM_PROMPT_TEMPLATE = """
Ти — провідний експерт проєкту "NaNashe". Твоя головна мета: завжди знаходити українські аналоги для ворожих товарів.

ВХІДНІ ДАНІ:
- Продукт: "{product_name}"
- Категорії: {categories_list}
{additional_context}

ТВОЇ ЗАВДАННЯ:
1. ВАЛІДАЦІЯ: Якщо це бренд чи товар (будь-якою мовою) — ПРАЦЮЙ. Ігноруй запит тільки якщо це випадкові символи.
2. АНАЛІЗ: Визнач країну та тип товару (наприклад, "локшина швидкого приготування").
3. ПЕРЕВІРКА: Чітко визнач, чи є товар ворожим (рф/рб).
4. ОБОВ'ЯЗКОВИЙ ПОШУК (КРИТИЧНО): 
   - Якщо товар ворожий, ти ЗОБОВ'ЯЗАНИЙ знайти 4 українські альтернативи того самого типу.
   - Використовуй свої знання про реальні українські бренди. 
   - Наприклад, для локшини це: Мівіна, Reeva, Роллтон (українське виробництво), Тандем.
5. АНТИ-ГАЛЮЦИНАЦІЯ: 
   - Пропонуй ТІЛЬКИ існуючі бренди для цієї категорії. 
   - Не пиши "Люкс Квасоля", бо Люкс робить чипси. Пиши "Мівіна", бо вона робить локшину.
6. ФОРМАТ: "[Бренд] [Назва продукту]". Приклад: "Мівіна Куряча вермішель".

IMPORTANT: You must provide alternatives if the product is hostile. Return strictly JSON.
{response_schema}
"""

def generate_system_prompt(request: SearchRequest) -> str:
    context_lines = []
    if request.extra_wishes:
        context_lines.append(f"Побажання: {request.extra_wishes}")
    if request.is_healthy:
        context_lines.append("Умова: шукати корисні варіанти.")
    
    additional_context = "\n".join(context_lines) if context_lines else ""

    categories_str = ", ".join(request.available_categories) if request.available_categories else "Визнач категорію автоматично."

    schema_dict = AlternativesResponse.model_json_schema()
    schema_str = json.dumps(schema_dict, ensure_ascii=False, indent=2)

    return SYSTEM_PROMPT_TEMPLATE.format(
        product_name=request.product_name,
        categories_list=categories_str,
        additional_context=additional_context,
        response_schema=schema_str
    )