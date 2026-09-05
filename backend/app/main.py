from fastapi import FastAPI

app = FastAPI(
    title="DevAssist API",
    description="Backend API for the DevAssist AI Developer Productivity Assistant.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "DevAssist API",
    }