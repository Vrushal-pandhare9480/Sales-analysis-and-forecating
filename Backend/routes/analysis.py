from fastapi import APIRouter
from sqlalchemy import text
from database import engine
import pandas as pd
from fastapi import Query

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.get("/category")
def category_sales():

    with engine.connect() as conn:

        result = conn.execute(text("""

            SELECT Category,
                   ROUND(SUM(Sales),2) AS Sales
            FROM sales
            GROUP BY Category

        """))

        data = []

        for row in result:

            data.append({
                "category": row[0],
                "sales": float(row[1])
            })

        return data
@router.get("/region")
def region_sales():

    with engine.connect() as conn:

        result = conn.execute(text("""

            SELECT Region,
                   ROUND(SUM(Sales),2) AS Sales
            FROM sales
            GROUP BY Region

        """))

        data = []

        for row in result:

            data.append({
                "region": row[0],
                "sales": float(row[1])
            })

        return data
@router.get("/monthly-sales")
def monthly_sales():

    with engine.connect() as conn:

        result = conn.execute(text("""

            SELECT
                MONTHNAME(`Order Date`) AS Month,
                MONTH(`Order Date`) AS MonthNo,
                ROUND(SUM(Sales),2) AS Sales

            FROM sales

            GROUP BY
                MONTH(`Order Date`),
                MONTHNAME(`Order Date`)

            ORDER BY MonthNo

        """))

        data = []

        for row in result:

            data.append({
                "month": row[0],
                "sales": float(row[2])
            })

        return data

@router.get("/top-products")
def top_products():

    query = """
    SELECT
        `Product Name`,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY `Product Name`
    ORDER BY Sales DESC
    LIMIT 10
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/top-customers")
def top_customers():

    query = """
    SELECT
        `Customer Name`,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY `Customer Name`
    ORDER BY Sales DESC
    LIMIT 10
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/forecast-data")
def forecast_data():

    try:

        forecast_df = predict_next_6_months()

        return forecast_df.to_dict(
            orient="records"
        )

    except Exception as e:

        return {
            "error": str(e)
        }

@router.get("/forecast-accuracy")
def forecast_accuracy():

    try:

        actual_query = """
        SELECT
            YEAR(`Order Date`) AS year,
            MONTH(`Order Date`) AS month,
            SUM(Sales) AS Actual_Sales
        FROM sales
        GROUP BY
            YEAR(`Order Date`),
            MONTH(`Order Date`)
        ORDER BY
            year,
            month
        """

        actual_df = pd.read_sql(
            actual_query,
            engine
        )

        forecast_query = """
        SELECT
            Month,
            Predicted_Sales
        FROM forecast
        """

        forecast_df = pd.read_sql(
            forecast_query,
            engine
        )

        print("ACTUAL DATA:")
        print(actual_df.head())

        print("FORECAST DATA:")
        print(forecast_df.head())

        if actual_df.empty or forecast_df.empty:

            return {
                "accuracy": 0,
                "message": "Actual or forecast data is empty"
            }

        # Convert forecast Month to datetime
        forecast_df["Month"] = pd.to_datetime(
            forecast_df["Month"]
        )

        forecast_df["year"] = (
            forecast_df["Month"].dt.year
        )

        forecast_df["month"] = (
            forecast_df["Month"].dt.month
        )

        merged_df = pd.merge(
            actual_df,
            forecast_df,
            on=["year", "month"],
            how="inner"
        )

        print("MATCHED DATA:")
        print(merged_df.head())

        if merged_df.empty:

            return {
                "accuracy": 0,
                "message": "No matching months found"
            }

        merged_df = merged_df[
            merged_df["Actual_Sales"] != 0
        ]

        mape = (
            abs(
                (
                    merged_df["Actual_Sales"]
                    -
                    merged_df["Predicted_Sales"]
                )
                /
                merged_df["Actual_Sales"]
            ).mean()
            * 100
        )

        accuracy = 100 - mape

        return {
            "accuracy": round(
                max(0, accuracy),
                2
            )
        }

    except Exception as e:

        return {
            "error": str(e)
        }

@router.get("/sales-data")
def sales_data(
    offset: int = Query(0, ge=0),
    limit: int = Query(70, ge=1, le=500)
):
    query = """
    SELECT
        `Order ID`,
        `Product Name`,
        Category,
        Region,
        Sales,
        Profit
    FROM sales
    ORDER BY `Order Date` DESC
    LIMIT :limit OFFSET :offset
    """

    df = pd.read_sql(
        text(query),
        engine,
        params={
            "limit": limit,
            "offset": offset
        }
    )

    return df.to_dict(orient="records")

@router.get("/customer-summary")
def customer_summary():

    total_query = """
    SELECT COUNT(DISTINCT `Customer ID`) AS TotalCustomers
    FROM sales
    """

    repeat_query = """
    SELECT COUNT(*) AS RepeatCustomers
    FROM (
        SELECT `Customer ID`
        FROM sales
        GROUP BY `Customer ID`
        HAVING COUNT(`Order ID`) > 1
    ) t
    """

    total = pd.read_sql(total_query, engine).iloc[0]["TotalCustomers"]

    repeat = pd.read_sql(repeat_query, engine).iloc[0]["RepeatCustomers"]

    new = total - repeat

    retention = round((repeat / total) * 100, 2)

    return {
        "TotalCustomers": int(total),
        "NewCustomers": int(new),
        "RepeatCustomers": int(repeat),
        "RetentionRate": retention
    }

@router.get("/customers-region")
def customers_region():

    query = """
    SELECT
        Region,
        COUNT(DISTINCT `Customer Name`) AS Customers
    FROM sales
    GROUP BY Region
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/customer-growth")
def customer_growth():

    query = """
    SELECT
        MONTHNAME(`Order Date`) AS Month,
        MONTH(`Order Date`) AS MonthNo,
        COUNT(DISTINCT `Customer Name`) AS Customers
    FROM sales
    GROUP BY MONTH(`Order Date`), MONTHNAME(`Order Date`)
    ORDER BY MonthNo
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/customers")
def customers(
    limit: int = Query(10),
    search: str = Query(""),
    region: str = Query(""),
    segment: str = Query("")
):

    query = """
    SELECT
        `Customer Name`,
        Segment,
        Region,
        COUNT(`Order ID`) AS Orders,
        SUM(Sales) AS Sales,
        SUM(Profit) AS Profit
    FROM sales
    WHERE `Customer Name` LIKE :search
    AND (:region = '' OR Region = :region)
    AND (:segment = '' OR Segment = :segment)
    GROUP BY
        `Customer Name`,
        Segment,
        Region
    ORDER BY Sales DESC
    LIMIT :limit
    """

    df = pd.read_sql(
        text(query),
        engine,
        params={
        "search": f"%{search}%",
        "region": region,
        "segment": segment,
        "limit": limit
}
    )

    return df.to_dict(orient="records")

@router.get("/product-summary")
def product_summary():

    total_products_query = """
    SELECT COUNT(DISTINCT `Product Name`) AS TotalProducts
    FROM sales
    """

    total_categories_query = """
    SELECT COUNT(DISTINCT Category) AS TotalCategories
    FROM sales
    """

    best_product_query = """
    SELECT `Product Name`
    FROM sales
    GROUP BY `Product Name`
    ORDER BY SUM(Sales) DESC
    LIMIT 1
    """

    avg_sales_query = """
    SELECT ROUND(AVG(Sales),2) AS AvgSales
    FROM sales
    """

    total_products = pd.read_sql(total_products_query, engine).iloc[0]["TotalProducts"]

    total_categories = pd.read_sql(total_categories_query, engine).iloc[0]["TotalCategories"]

    best_product = pd.read_sql(best_product_query, engine).iloc[0]["Product Name"]

    avg_sales = pd.read_sql(avg_sales_query, engine).iloc[0]["AvgSales"]

    return {
        "TotalProducts": int(total_products),
        "TotalCategories": int(total_categories),
        "BestProduct": best_product,
        "AvgSales": float(avg_sales)
    }

@router.get("/product-summary")
def product_summary():

    total_products_query = """
    SELECT COUNT(DISTINCT `Product Name`) AS TotalProducts
    FROM sales
    """

    total_categories_query = """
    SELECT COUNT(DISTINCT Category) AS TotalCategories
    FROM sales
    """

    best_product_query = """
    SELECT `Product Name`
    FROM sales
    GROUP BY `Product Name`
    ORDER BY SUM(Sales) DESC
    LIMIT 1
    """

    avg_sales_query = """
    SELECT ROUND(AVG(Sales),2) AS AvgSales
    FROM sales
    """

    total_products = pd.read_sql(total_products_query, engine).iloc[0]["TotalProducts"]

    total_categories = pd.read_sql(total_categories_query, engine).iloc[0]["TotalCategories"]

    best_product = pd.read_sql(best_product_query, engine).iloc[0]["Product Name"]

    avg_sales = pd.read_sql(avg_sales_query, engine).iloc[0]["AvgSales"]

    return {
        "TotalProducts": int(total_products),
        "TotalCategories": int(total_categories),
        "BestProduct": best_product,
        "AvgSales": float(avg_sales)
    }

@router.get("/products")
def products(
    limit: int = Query(10),
    search: str = Query(""),
    category: str = Query("")
):

    query = """
    SELECT
        `Product Name`,
        Category,
        SUM(Sales) AS Sales,
        SUM(Profit) AS Profit,
        SUM(Quantity) AS Quantity
    FROM sales
    WHERE `Product Name` LIKE :search
    AND (:category = '' OR Category = :category)
    GROUP BY
        `Product Name`,
        Category
    ORDER BY Sales DESC
    LIMIT :limit
    """

    df = pd.read_sql(
        text(query),
        engine,
        params={
            "search": f"%{search}%",
            "category": category,
            "limit": limit
        }
    )

    return df.to_dict(orient="records")

@router.get("/product-categories")
def product_categories():

    query = """
    SELECT DISTINCT Category
    FROM sales
    WHERE Category IS NOT NULL
    ORDER BY Category
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/category-sales")
def category_sales():

    query = """
    SELECT
        Category,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Category
    ORDER BY Sales DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/region-summary")
def region_summary():

    query = """
    SELECT
        Region,
        SUM(Sales) AS Sales,
        SUM(Profit) AS Profit,
        COUNT(`Order ID`) AS Orders
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    df = pd.read_sql(query, engine)

    total_regions = df["Region"].nunique()

    best_region = df.iloc[0]["Region"]

    highest_sales = df["Sales"].max()

    highest_profit = df["Profit"].max()

    return {
        "TotalRegions": int(total_regions),
        "BestRegion": best_region,
        "HighestSales": float(highest_sales),
        "HighestProfit": float(highest_profit)
    }

@router.get("/region-sales")
def region_sales():

    query = """
    SELECT
        Region,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/region-performance")
def region_performance():

    query = """
    SELECT
        Region,
        SUM(Sales) AS Sales,
        SUM(Profit) AS Profit,
        COUNT(`Order ID`) AS Orders
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/region-profit")
def region_profit():

    query = """
    SELECT
        Region,
        SUM(Profit) AS Profit
    FROM sales
    GROUP BY Region
    ORDER BY Profit DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")



@router.get("/dashboard-kpi")
def dashboard_kpi():

    query = """
    SELECT
        SUM(Sales) AS total_sales,
        SUM(Profit) AS total_profit,
        COUNT(DISTINCT `Order ID`) AS total_orders,
        COUNT(DISTINCT `Customer Name`) AS total_customers
    FROM sales
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")[0]

@router.get("/category-sales")
def category_sales():

    query = """
    SELECT
        Category,
        SUM(Sales) AS total_sales
    FROM sales
    GROUP BY Category
    ORDER BY total_sales DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

# @router.get("/region-sales")
# def region_sales():

#     query = """
#     SELECT
#         Region,
#         SUM(Sales) AS total_sales
#     FROM sales
#     GROUP BY Region
#     ORDER BY total_sales DESC
#     """

#     df = pd.read_sql(query, engine)

#     return df.to_dict(orient="records")

@router.get("/monthly-sales")
def monthly_sales():

    query = """
    SELECT
        DATE_FORMAT(`Order Date`, '%Y-%m') AS month,
        SUM(Sales) AS sales
    FROM sales
    GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')
    ORDER BY month
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/customer-kpis")
def customer_kpis():

    query = """
    SELECT

        COUNT(DISTINCT `Customer ID`) AS total_customers,

        COUNT(
            DISTINCT CASE
                WHEN `Order Date` >= DATE_SUB(
                    (SELECT MAX(`Order Date`) FROM sales),
                    INTERVAL 30 DAY
                )
                THEN `Customer ID`
            END
        ) AS new_customers,

        COUNT(
            DISTINCT CASE
                WHEN `Customer ID` IN (
                    SELECT `Customer ID`
                    FROM sales
                    GROUP BY `Customer ID`
                    HAVING COUNT(DISTINCT `Order ID`) > 1
                )
                THEN `Customer ID`
            END
        ) AS repeat_customers

    FROM sales
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")[0]

@router.get("/customers-by-region")
def customers_by_region():

    query = """
    SELECT
        Region,
        COUNT(DISTINCT `Customer ID`) AS customers
    FROM sales
    GROUP BY Region
    ORDER BY customers DESC
    """

    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")

@router.get("/region-kpis")
def region_kpis():

    query = """
    SELECT
        Region,
        SUM(Sales) AS total_sales,
        SUM(Profit) AS total_profit
    FROM sales
    GROUP BY Region
    ORDER BY total_sales DESC
    """

    df = pd.read_sql(query, engine)

    best_region = df.iloc[0]["Region"]

    return {
        "best_region": best_region,
        "total_regions": len(df),
        "highest_sales": round(
            float(df["total_sales"].max()), 2
        ),
        "highest_profit": round(
            float(df["total_profit"].max()), 2
        )
    }

@router.get("/sales-kpis")
def sales_kpis():

    query = """
    SELECT
        SUM(Sales) AS total_sales,
        SUM(Profit) AS total_profit,
        COUNT(DISTINCT `Order ID`) AS total_orders,
        AVG(Discount) AS average_discount
    FROM sales
    """

    df = pd.read_sql(query, engine)

    return {
        "total_sales": float(df.iloc[0]["total_sales"]),
        "total_profit": float(df.iloc[0]["total_profit"]),
        "total_orders": int(df.iloc[0]["total_orders"]),
        "average_discount": float(df.iloc[0]["average_discount"])
    }

@router.get("/business-insights")
def business_insights():

    try:

        # -----------------------------
        # Monthly Sales
        # -----------------------------

        monthly_query = """
        SELECT
            YEAR(`Order Date`) AS year,
            MONTH(`Order Date`) AS month,
            SUM(Sales) AS sales
        FROM sales
        GROUP BY
            YEAR(`Order Date`),
            MONTH(`Order Date`)
        ORDER BY
            year,
            month
        """

        monthly_df = pd.read_sql(monthly_query, engine)

        # -----------------------------
        # Category Sales
        # -----------------------------

        category_query = """
        SELECT
            Category,
            SUM(Sales) AS sales
        FROM sales
        GROUP BY Category
        ORDER BY sales DESC
        """

        category_df = pd.read_sql(category_query, engine)

        # -----------------------------
        # Region Profit
        # -----------------------------

        region_query = """
        SELECT
            Region,
            SUM(Profit) AS profit
        FROM sales
        GROUP BY Region
        ORDER BY profit DESC
        """

        region_df = pd.read_sql(region_query, engine)

        # -----------------------------
        # Average Discount
        # -----------------------------

        discount_query = """
        SELECT AVG(Discount) AS average_discount
        FROM sales
        """

        discount_df = pd.read_sql(discount_query, engine)

        # -----------------------------
        # Sales Growth
        # -----------------------------

        if len(monthly_df) >= 2:

            latest = monthly_df.iloc[-1]
            previous = monthly_df.iloc[-2]

            latest_sales = float(latest["sales"])
            previous_sales = float(previous["sales"])

            if previous_sales != 0:

                growth = (
                    (latest_sales - previous_sales)
                    / previous_sales
                ) * 100

            else:
                growth = 0

            growth_text = (
                f"Sales {'increased' if growth >= 0 else 'decreased'} "
                f"by {abs(growth):.1f}% compared to the previous month."
            )

        else:

            growth_text = "Monthly sales data is not sufficient for comparison."

        # -----------------------------
        # Best Category
        # -----------------------------

        best_category = category_df.iloc[0]["Category"]

        # -----------------------------
        # Best Region
        # -----------------------------

        best_region = region_df.iloc[0]["Region"]

        # -----------------------------
        # Average Discount
        # -----------------------------

        avg_discount = float(
            discount_df.iloc[0]["average_discount"]
        ) * 100

        # -----------------------------
        # Final Insights
        # -----------------------------

        insights = [

            growth_text,

            f"{best_category} category generated the highest sales.",

            f"{best_region} region generated the highest profit.",

            f"Average discount across all sales is {avg_discount:.1f}%."

        ]

        return {
            "insights": insights
        }

    except Exception as e:

        return {
            "error": str(e)
        }