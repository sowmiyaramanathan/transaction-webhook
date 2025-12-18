import os
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.environ["REDIS_URL"]
DATABASE_URL = os.environ["DATABASE_URL"]