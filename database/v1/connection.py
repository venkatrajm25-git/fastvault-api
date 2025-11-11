import os

env = os.getenv("FASTAPI_ENV", "development")

if env == "testing":
    from config.v1.config_test import getDBConnection
elif env == "production":
    from config.v1.config_prod import getDBConnection
else:
    from config.v1.config_dev import getDBConnection
