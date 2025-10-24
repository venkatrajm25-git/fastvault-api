from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()


env = os.getenv("FASTAPI_ENV", "development")
if env == "testing":
    load_dotenv(".env.test")
elif env == "production":
    load_dotenv(".env.prod")
else:
    pass

print("Current Environment:", env.capitalize())

app = FastAPI()


@app.get("/")
async def home():
    return JSONResponse(
        content={"success": True, "message": "FastVaultAPI is working", "env": env}
    )
