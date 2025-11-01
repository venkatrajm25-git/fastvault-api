import os

env = os.getenv("FASTAPI_ENV")
if env == "testing":
    from config.v1.config_test import Base
elif env == "production":
    from config.v1.config_prod import Base
else:
    from config.v1.config_dev import Base
