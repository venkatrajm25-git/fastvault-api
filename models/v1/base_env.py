import os

env = os.getenv("FASTAPI_ENV")
if env == "testing":
    from configs.v1.testing_db import Base
elif env == "production":
    from configs.v1.production_db import Base
else:
    from configs.v1.db import Base
