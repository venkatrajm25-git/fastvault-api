import os


class Config:
    # DB
    DB_USER = os.getenv("USER", "postgres")
    DB_PASSWORD = os.getenv("PWD", "81900Vr#")
    DB_HOST = os.getenv("HOST", "localhost")
    DB_PORT = os.getenv("PORT", 5432)
    DB_DBNAME = os.getenv("DBNAME", "fastvault_dev")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


class TestingConfig:
    # DB
    DB_USER = os.getenv("USER", "postgres")
    DB_PASSWORD = os.getenv("PWD", "81900Vr#")
    DB_HOST = os.getenv("HOST", "localhost")
    DB_PORT = os.getenv("PORT", 5432)
    DB_DBNAME = os.getenv("DBNAME", "fastvault_test")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


class ProductionConfig:
    # DB
    DB_USER = os.getenv("USER", "postgres")
    DB_PASSWORD = os.getenv("PWD", "81900Vr#")
    DB_HOST = os.getenv("HOST", "localhost")
    DB_PORT = os.getenv("PORT", 5432)
    DB_DBNAME = os.getenv("DBNAME", "fastvault_prod")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DBNAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
