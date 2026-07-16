# Minimal API placeholder (not started by default)
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
async def root():
    return {"status": "SPACE_BOUND_AI API placeholder"}
