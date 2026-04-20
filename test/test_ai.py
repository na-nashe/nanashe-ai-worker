import pytest
from ai_service import generate_alternative
from models import SearchRequest

def get_validation_cases():
    return [
       
        {
            "name": "asdfghjkl",
            "categories": ["food", "soft"],
            "expected_message_contains": "не розпізнано"
        },
       
        {
            "name": "iPhone",
            "categories": ["electronics", "soft"],
            "expected_message_contains": "не є ворожим"
        }
    ]

@pytest.mark.parametrize("case", get_validation_cases())
def test_ai_validation_logic(case):
    request = SearchRequest(
        product_name=case["name"],
        available_categories=case["categories"]
    )
    
    response = generate_alternative(request)
    
    assert response.message is not None
    assert case["expected_message_contains"].lower() in response.message.lower()
    assert len(response.alternatives) == 0  