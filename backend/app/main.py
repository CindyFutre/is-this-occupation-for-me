from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


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