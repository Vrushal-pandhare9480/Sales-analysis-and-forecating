import pandas as pd
from sqlalchemy import create_engine
from config import *

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

# CSV Read
df = pd.read_csv("data/Sample - Superstore.csv", encoding="latin1")

# Date conversion
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

# Import into MySQL
df.to_sql(
    "sales",
    con=engine,
    if_exists="replace",
    index=False
)

print("✅ Data Imported Successfully!")
print(df.head())
