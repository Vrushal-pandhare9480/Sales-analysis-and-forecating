from sqlalchemy import create_engine
from config import *

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

connection = engine.connect()

print("Database Connected Successfully!")