import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import text
from database import engine


def load_monthly_sales():

    query = """

    SELECT

        MONTH(`Order Date`) AS MonthNo,

        MONTHNAME(`Order Date`) AS Month,

        SUM(Sales) AS Sales

    FROM sales

    GROUP BY

        MONTH(`Order Date`),

        MONTHNAME(`Order Date`)

    ORDER BY MonthNo

    """

    df = pd.read_sql(query, engine)

    return df


def train_model():

    df = load_monthly_sales()

    X = df[["MonthNo"]]

    y = df["Sales"]

    model = LinearRegression()

    model.fit(X, y)

    return model


def predict_next_6_months():

    model = train_model()

    future_months = pd.DataFrame({
        "MonthNo": [13, 14, 15, 16, 17, 18]
    })

    predictions = model.predict(future_months)

    month_names = [
        "Next Jan",
        "Next Feb",
        "Next Mar",
        "Next Apr",
        "Next May",
        "Next Jun"
    ]

    result = pd.DataFrame({
        "Month": month_names,
        "Predicted_Sales": predictions.round(2)
    })

    # Make sure forecast table exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS forecast (
        Month VARCHAR(50),
        Predicted_Sales DECIMAL(15,2)
    )
    """

    with engine.begin() as conn:

        conn.execute(text(create_table_query))

        # Remove old forecast data
        conn.execute(text("DELETE FROM forecast"))

    # Save new forecast data
    result.to_sql(
        "forecast",
        engine,
        if_exists="append",
        index=False
    )

    return result


if __name__ == "__main__":

    forecast = predict_next_6_months()

    print("Forecast Saved Successfully ✅")

    print("\nNext 6 Months Forecast\n")

    print(forecast)