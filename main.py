from fastapi import FastAPI
from fastapi.responses import JSONResponse
from config.v1.env_loader import load_environment

# --- load env
load_environment()

app = FastAPI(redoc_url=False)


from routes.v1.route_register import register_routes
from core.v1.exception_handler import register_exception_handlers

register_routes(app)

register_exception_handlers(app)


@app.get("/")
async def home():
    return JSONResponse(content={"success": True, "message": "FastVaultAPI is working"})
