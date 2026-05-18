from fastapi import FastAPI
from dotenv import load_dotenv


load_dotenv()


from ai_service import router as ai_router

app = FastAPI()


app.include_router(ai_router)

@app.get("/")
def root():
    return {"message": "Server is running! Go to /docs to test."}