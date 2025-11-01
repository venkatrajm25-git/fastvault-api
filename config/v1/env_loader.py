import os
from dotenv import load_dotenv


def load_environment():
    env = os.getenv("FASTAPI_ENV", "development")
    if env == "testing":
        load_dotenv(".env.test")
    elif env == "production":
        load_dotenv(".env.prod")
    else:
        load_dotenv(".env")

    print("Current Environment:", env.capitalize())
