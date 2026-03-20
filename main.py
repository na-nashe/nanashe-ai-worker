import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class AlternativeResult(BaseModel):
    name: str
    description: str
    url: Optional[str]
    aliases: List[str]

class SearchRequest(BaseModel):
    product_name: str

@app.get("/")
def root():
    return {"message": "Server is running! Go to /docs to test."}

@app.post("/api/v1/generate")
def generate_alternative(request: SearchRequest):
    print(f"Request for: {request.product_name}")
    mock_data = {
        "name": "MASTER:Accounting",
        "description": "Ukrainian alternative for accounting. (Test Mode)",
        "url": "https://masterbuh.com/",
        "aliases": ["Master", "BAS", "1C alternative"]
    }
    java_url = os.getenv("JAVA_SERVER_URL", "http://localhost:8080/api/alternatives")
    try:
        response = requests.post(java_url, json=mock_data, timeout=5)
        java_status = "Sent to Java" if response.ok else f"Java Error: {response.status_code}"
    except:
        java_status = "Java Offline"
    return {"status": "success", "java_status": java_status, "data": mock_data}