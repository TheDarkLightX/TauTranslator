from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    print("Attempting to run minimal FastAPI app with Uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
