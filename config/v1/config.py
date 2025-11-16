import os


class Config:
    # DB
    DB_USER = os.getenv("USER")
    DB_PASSWORD = os.getenv("PWD")
    DB_HOST = os.getenv("HOST")
    DB_PORT = os.getenv("PORT")
    DB_DBNAME = os.getenv("DBNAME")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

    FRONTEND_URL = os.getenv("FRONTEND_URL")
    # SMTP
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


class TestingConfig:
    # DB
    DB_USER = os.getenv("USER")
    DB_PASSWORD = os.getenv("PWD")
    DB_HOST = os.getenv("HOST")
    DB_PORT = os.getenv("PORT")
    DB_DBNAME = os.getenv("DBNAME")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    FRONTEND_URL = os.getenv("FRONTEND_URL")


class ProductionConfig:
    # DB
    DB_USER = os.getenv("USER")
    DB_PASSWORD = os.getenv("PWD")
    DB_HOST = os.getenv("HOST")
    DB_PORT = os.getenv("PORT")
    DB_DBNAME = os.getenv("DBNAME")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
