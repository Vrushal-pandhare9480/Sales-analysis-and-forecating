from fastapi import APIRouter
from sqlalchemy import text
from database import engine

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary():

    with engine.connect() as conn:

        total_sales = conn.execute(
            text("SELECT SUM(Sales) FROM sales")
        ).scalar()

        total_profit = conn.execute(
            text("SELECT SUM(Profit) FROM sales")
        ).scalar()

        total_orders = conn.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar()

        avg_discount = conn.execute(
            text("SELECT AVG(Discount) FROM sales")
        ).scalar()

    return {

        "total_sales": round(total_sales,2),

        "total_profit": round(total_profit,2),

        "total_orders": total_orders,

        "avg_discount": round(avg_discount*100,2)

    }