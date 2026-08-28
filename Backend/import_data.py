from database import engine
import pandas as pd
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import BigInteger, Text, DateTime, Float

# CSV Read
df = pd.read_csv("data/Sample - Superstore.csv", encoding="latin1")

# Date conversion
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

metadata = MetaData()

sales_table = Table(
    "sales",
    metadata,

    Column("Row ID", BigInteger, primary_key=True),
    Column("Order ID", Text),
    Column("Order Date", DateTime),
    Column("Ship Date", DateTime),
    Column("Ship Mode", Text),
    Column("Customer ID", Text),
    Column("Customer Name", Text),
    Column("Segment", Text),
    Column("Country", Text),
    Column("City", Text),
    Column("State", Text),
    Column("Postal Code", BigInteger),
    Column("Region", Text),
    Column("Product ID", Text),
    Column("Category", Text),
    Column("Sub-Category", Text),
    Column("Product Name", Text),
    Column("Sales", Float),
    Column("Quantity", BigInteger),
    Column("Discount", Float),
    Column("Profit", Float),
)

# Existing sales table delete करून नवीन table create
metadata.drop_all(engine, tables=[sales_table])
metadata.create_all(engine)

# Data insert
df.to_sql(
    "sales",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Data Imported Successfully!")
print(df.head())