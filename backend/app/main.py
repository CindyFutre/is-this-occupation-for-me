from fastapi import FastAPI
from app.db.mongodb import connect_to_mongo, close_mongo_connection

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    try:
        await connect_to_mongo()
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    print("Disconnected from MongoDB")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}