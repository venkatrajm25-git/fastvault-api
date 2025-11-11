from fastapi import FastAPI
from fastapi.responses import JSONResponse
from config.v1.env_loader import load_environment

# --- load env
load_environment()

app = FastAPI(redoc_url=False)


from routes.v1.route_register import register_routes
from core.v1.exception_handler import register_exception_handlers

register_routes(app)
print("✅ Routes registered successfully")

register_exception_handlers(app)


@app.get("/")
async def home():
    return JSONResponse(content={"success": True, "message": "FastVaultAPI is working"})


import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render gives this env variable
    uvicorn.run("main:app", host="0.0.0.0", port=port)
