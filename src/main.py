from fastapi import FastAPI

app = FastAPI(title="Price Tracker API")

@app.get("/")
async def root():
    return {"message": "Hello Server World"}
