from fastapi import APIRouter
from fastapi.responses import FileResponse

import pandas as pd
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from database import engine

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/sales-csv")
def download_sales_csv():

    query = "SELECT * FROM sales"

    df = pd.read_sql(query, engine)

    file_name = "sales_report.csv"

    df.to_csv(file_name, index=False)

    return FileResponse(
        path=file_name,
        filename=file_name,
        media_type="text/csv"
    )

@router.get("/dashboard-pdf")
def download_dashboard_pdf():

    pdf_file = "dashboard_report.pdf"

    chart_files = []

    # =========================================================
    # PDF SETUP
    # =========================================================

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    elements = []

    # =========================================================
    # TITLE
    # =========================================================

    elements.append(
        Paragraph(
            "<b>Dashboard Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated On : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    # =========================================================
    # 1. DASHBOARD KPIs
    # =========================================================

    kpi_query = """
    SELECT
        SUM(Sales) AS TotalSales,
        SUM(Profit) AS TotalProfit,
        COUNT(DISTINCT `Order ID`) AS TotalOrders,
        COUNT(DISTINCT `Customer ID`) AS TotalCustomers
    FROM sales
    """

    kpi_df = pd.read_sql(kpi_query, engine)

    total_sales = float(kpi_df["TotalSales"].iloc[0] or 0)
    total_profit = float(kpi_df["TotalProfit"].iloc[0] or 0)
    total_orders = int(kpi_df["TotalOrders"].iloc[0] or 0)
    total_customers = int(kpi_df["TotalCustomers"].iloc[0] or 0)

    kpi_data = [
        ["Total Sales", "Total Profit"],
        [
            f"₹{total_sales:,.2f}",
            f"₹{total_profit:,.2f}"
        ],
        ["Total Orders", "Customers"],
        [
            f"{total_orders:,}",
            f"{total_customers:,}"
        ]
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[250, 250]
    )

    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 2), (-1, 2), colors.white),

            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
    )

    elements.append(kpi_table)

    elements.append(Spacer(1, 20))

    # =========================================================
    # 2. CATEGORY ANALYSIS CHART
    # =========================================================

    category_query = """
    SELECT
        Category,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Category
    ORDER BY Sales DESC
    """

    category_df = pd.read_sql(category_query, engine)

    plt.figure(figsize=(7, 4))

    plt.bar(
        category_df["Category"],
        category_df["Sales"]
    )

    plt.title("Category Analysis")
    plt.xlabel("Category")
    plt.ylabel("Sales")

    plt.xticks(rotation=20)
    plt.tight_layout()

    category_chart = "dashboard_category.png"

    plt.savefig(
        category_chart,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    chart_files.append(category_chart)

    elements.append(
        Paragraph(
            "<b>Category Analysis</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            category_chart,
            width=480,
            height=270
        )
    )

    elements.append(Spacer(1, 15))

    # =========================================================
    # 3. FORECAST SALES CHART
    # =========================================================

    forecast_query = """
    SELECT
        Month,
        Predicted_Sales
    FROM forecast
    ORDER BY Month
    """

    try:

        forecast_df = pd.read_sql(
            forecast_query,
            engine
        )

    except Exception:

        forecast_df = pd.DataFrame()

    if not forecast_df.empty:

        plt.figure(figsize=(7, 4))

        plt.plot(
            forecast_df["Month"],
            forecast_df["Predicted_Sales"],
            marker="o"
        )

        plt.title("Forecast Sales")
        plt.xlabel("Month")
        plt.ylabel("Predicted Sales")

        plt.xticks(rotation=30)

        plt.tight_layout()

        forecast_chart = "dashboard_forecast.png"

        plt.savefig(
            forecast_chart,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        chart_files.append(forecast_chart)

        elements.append(
            Paragraph(
                "<b>Forecast Sales</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Image(
                forecast_chart,
                width=480,
                height=270
            )
        )

        elements.append(Spacer(1, 15))

    # =========================================================
    # 4. SALES TREND CHART
    # =========================================================

    monthly_query = """
    SELECT
        DATE_FORMAT(`Order Date`, '%%Y-%%m') AS Month,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY DATE_FORMAT(`Order Date`, '%%Y-%%m')
    ORDER BY Month
    """

    monthly_df = pd.read_sql(
        monthly_query,
        engine
    )

    plt.figure(figsize=(7, 4))

    plt.plot(
        monthly_df["Month"],
        monthly_df["Sales"],
        marker="o"
    )

    plt.title("Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Sales")

    plt.xticks(rotation=45)

    plt.tight_layout()

    sales_chart = "dashboard_sales_trend.png"

    plt.savefig(
        sales_chart,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    chart_files.append(sales_chart)

    elements.append(
        Paragraph(
            "<b>Sales Trend</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            sales_chart,
            width=480,
            height=270
        )
    )

    elements.append(Spacer(1, 15))

    # =========================================================
    # 5. REVENUE BY REGION
    # =========================================================

    region_query = """
    SELECT
        Region,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    region_df = pd.read_sql(
        region_query,
        engine
    )

    plt.figure(figsize=(7, 4))

    plt.bar(
        region_df["Region"],
        region_df["Sales"]
    )

    plt.title("Revenue by Region")
    plt.xlabel("Region")
    plt.ylabel("Sales")

    plt.xticks(rotation=20)

    plt.tight_layout()

    region_chart = "dashboard_region.png"

    plt.savefig(
        region_chart,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    chart_files.append(region_chart)

    elements.append(
        Paragraph(
            "<b>Revenue by Region</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            region_chart,
            width=480,
            height=270
        )
    )

    # =========================================================
    # BUILD PDF
    # =========================================================

    doc.build(elements)

    # =========================================================
    # CLEANUP CHART IMAGES
    # =========================================================

    for file in chart_files:

        if os.path.exists(file):

            os.remove(file)

    return FileResponse(
        pdf_file,
        filename="dashboard_report.pdf",
        media_type="application/pdf"
    )

@router.get("/forecast-csv")
def download_forecast_csv():

    query = """
    SELECT
        Month,
        Predicted_Sales
    FROM forecast
    """

    df = pd.read_sql(query, engine)

    file_name = "forecast_report.csv"

    df.to_csv(file_name, index=False)

    return FileResponse(
        path=file_name,
        filename=file_name,
        media_type="text/csv"
    )


@router.get("/region-pdf")
def download_product_pdf():

    file_path = "Region_analysis_report.pdf"

    # -----------------------------
    # REGION DATA
    # -----------------------------

    region_query = """
        SELECT
            Region,
            SUM(Sales) AS Sales,
            SUM(Profit) AS Profit,
            COUNT(`Order ID`) AS Orders
        FROM sales
        GROUP BY Region
        ORDER BY Sales DESC
    """

    region_df = pd.read_sql(region_query, engine)

    if region_df.empty:
        return {"message": "No region data found"}

    # -----------------------------
    # KPI DATA
    # -----------------------------

    best_region = region_df.iloc[0]["Region"]

    total_regions = region_df["Region"].nunique()

    highest_sales = float(region_df["Sales"].max())

    highest_profit = float(region_df["Profit"].max())

    # -----------------------------
    # SALES CHART
    # -----------------------------

    sales_chart = "region_sales_chart.png"

    plt.figure(figsize=(8, 4))

    plt.bar(
        region_df["Region"],
        region_df["Sales"]
    )

    plt.title("Region Wise Sales")

    plt.xlabel("Region")
    plt.ylabel("Sales")

    plt.tight_layout()

    plt.savefig(
        sales_chart,
        dpi=150
    )

    plt.close()

    # -----------------------------
    # PROFIT CHART
    # -----------------------------

    profit_chart = "region_profit_chart.png"

    plt.figure(figsize=(8, 4))

    plt.bar(
        region_df["Region"],
        region_df["Profit"]
    )

    plt.title("Profit by Region")

    plt.xlabel("Region")
    plt.ylabel("Profit")

    plt.tight_layout()

    plt.savefig(
        profit_chart,
        dpi=150
    )

    plt.close()

    # -----------------------------
    # PDF
    # -----------------------------

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Regional Analysis Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 15))

    # -----------------------------
    # KPI TABLE
    # -----------------------------

    kpi_data = [
        ["KPI", "Value"],
        ["Best Region", str(best_region)],
        ["Total Regions", str(total_regions)],
        ["Highest Sales", f"₹{highest_sales:,.2f}"],
        ["Highest Profit", f"₹{highest_profit:,.2f}"]
    ]

    kpi_table = Table(kpi_data)

    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(kpi_table)

    elements.append(Spacer(1, 20))

    # -----------------------------
    # SALES CHART
    # -----------------------------

    elements.append(
        Paragraph(
            "Region Wise Sales Chart",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            sales_chart,
            width=6.5 * inch,
            height=3.2 * inch
        )
    )

    elements.append(Spacer(1, 20))

    # -----------------------------
    # PROFIT CHART
    # -----------------------------

    elements.append(
        Paragraph(
            "Profit by Region",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            profit_chart,
            width=6.5 * inch,
            height=3.2 * inch
        )
    )

    elements.append(Spacer(1, 20))

    # -----------------------------
    # REGION PERFORMANCE TABLE
    # -----------------------------

    elements.append(
        Paragraph(
            "Region Performance",
            styles["Heading2"]
        )
    )

    table_data = [
        ["Region", "Sales", "Profit", "Orders"]
    ]

    for _, row in region_df.iterrows():

        table_data.append([
            row["Region"],
            f"₹{float(row['Sales']):,.2f}",
            f"₹{float(row['Profit']):,.2f}",
            str(int(row["Orders"]))
        ])

    region_table = Table(table_data)

    region_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )

    elements.append(region_table)

    # -----------------------------
    # BUILD PDF
    # -----------------------------

    doc.build(elements)

    # -----------------------------
    # RETURN PDF
    # -----------------------------

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="Region_Analysis_Report.pdf"
    )

@router.get("/sales-analysis-pdf")
def download_sales_analysis_pdf():

    pdf_file = "sales_analysis_report.pdf"

    # ==================================================
    # 1. KPI DATA
    # ==================================================

    kpi_query = """
    SELECT
        SUM(Sales) AS TotalSales,
        SUM(Profit) AS TotalProfit,
        COUNT(DISTINCT `Order ID`) AS TotalOrders,
        AVG(Discount) AS AverageDiscount
    FROM sales
    """

    kpi = pd.read_sql(kpi_query, engine)

    total_sales = float(kpi["TotalSales"][0] or 0)
    total_profit = float(kpi["TotalProfit"][0] or 0)
    total_orders = int(kpi["TotalOrders"][0] or 0)
    avg_discount = float(kpi["AverageDiscount"][0] or 0)


    # ==================================================
    # 2. CATEGORY DATA
    # ==================================================

    category_query = """
    SELECT
        Category,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Category
    ORDER BY Sales DESC
    """

    category_df = pd.read_sql(
        category_query,
        engine
    )


    # ==================================================
    # 3. REGION DATA
    # ==================================================

    region_query = """
    SELECT
        Region,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    region_df = pd.read_sql(
        region_query,
        engine
    )


    # ==================================================
    # 4. MONTHLY SALES
    # ==================================================

    monthly_query = """
        SELECT
            DATE_FORMAT(`Order Date`, '%%Y-%%m') AS Month,
            SUM(Sales) AS Sales
        FROM sales
        GROUP BY DATE_FORMAT(`Order Date`, '%%Y-%%m')
        ORDER BY Month
        """

    monthly_df = pd.read_sql(
        monthly_query,
        engine
    )


    # ==================================================
    # 5. CREATE CATEGORY CHART
    # ==================================================

    category_chart = "sales_analysis_category.png"

    plt.figure(figsize=(7, 4))

    plt.pie(
        category_df["Sales"],
        labels=category_df["Category"],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Sales by Category")

    plt.tight_layout()

    plt.savefig(
        category_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 6. CREATE REGION CHART
    # ==================================================

    region_chart = "sales_analysis_region.png"

    plt.figure(figsize=(7, 4))

    plt.bar(
        region_df["Region"],
        region_df["Sales"]
    )

    plt.title("Sales by Region")

    plt.xlabel("Region")

    plt.ylabel("Sales")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        region_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 7. CREATE MONTHLY SALES CHART
    # ==================================================

    monthly_chart = "sales_analysis_monthly.png"

    plt.figure(figsize=(8, 4))

    plt.plot(
        monthly_df["Month"],
        monthly_df["Sales"],
        marker="o"
    )

    plt.title("Monthly Sales Trend")

    plt.xlabel("Month")

    plt.ylabel("Sales")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        monthly_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 8. CREATE PDF
    # ==================================================

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []


    # TITLE

    elements.append(
        Paragraph(
            "<b>Sales Analysis Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated On : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )


    # ==================================================
    # KPI TABLE
    # ==================================================

    kpi_data = [

        [
            "Total Sales",
            "Total Profit",
            "Total Orders",
            "Average Discount"
        ],

        [
            f"₹{total_sales:,.2f}",
            f"₹{total_profit:,.2f}",
            f"{total_orders:,}",
            f"{avg_discount * 100:.2f}%"
        ]

    ]


    kpi_table = Table(
        kpi_data,
        colWidths=[
            1.3 * inch,
            1.3 * inch,
            1.3 * inch,
            1.3 * inch
        ]
    )


    kpi_table.setStyle(
        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("BOX", (0, 0), (-1, -1), 1, colors.grey),

            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ("TOPPADDING", (0, 0), (-1, -1), 8),

        ])
    )


    elements.append(kpi_table)

    elements.append(
        Spacer(1, 20)
    )


    # ==================================================
    # CHARTS
    # ==================================================

    elements.append(
        Paragraph(
            "<b>Sales by Category</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            category_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )

    elements.append(
        Spacer(1, 15)
    )


    elements.append(
        Paragraph(
            "<b>Sales by Region</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            region_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )

    elements.append(
        Spacer(1, 15)
    )


    elements.append(
        Paragraph(
            "<b>Monthly Sales Trend</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            monthly_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )


    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(elements)


    # ==================================================
    # DELETE TEMP CHARTS
    # ==================================================

    for file in [
        category_chart,
        region_chart,
        monthly_chart
    ]:

        if os.path.exists(file):
            os.remove(file)


    return FileResponse(
        pdf_file,
        filename="sales-analysis_report.pdf",
        media_type="application/pdf"
    )


@router.get("/products-pdf")
def download_products_pdf():

    pdf_file = "products_report.pdf"

    # ==================================================
    # 1. KPI DATA
    # ==================================================

    kpi_query = """
    SELECT
        SUM(Sales) AS TotalSales,
        SUM(Profit) AS TotalProfit,
        COUNT(DISTINCT `Order ID`) AS TotalOrders,
        AVG(Discount) AS AverageDiscount
    FROM sales
    """

    kpi = pd.read_sql(kpi_query, engine)

    total_sales = float(kpi["TotalSales"][0] or 0)
    total_profit = float(kpi["TotalProfit"][0] or 0)
    total_orders = int(kpi["TotalOrders"][0] or 0)
    avg_discount = float(kpi["AverageDiscount"][0] or 0)


    # ==================================================
    # 2. CATEGORY DATA
    # ==================================================

    category_query = """
    SELECT
        Category,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Category
    ORDER BY Sales DESC
    """

    category_df = pd.read_sql(
        category_query,
        engine
    )


    # ==================================================
    # 3. REGION DATA
    # ==================================================

    region_query = """
    SELECT
        Region,
        SUM(Sales) AS Sales
    FROM sales
    GROUP BY Region
    ORDER BY Sales DESC
    """

    region_df = pd.read_sql(
        region_query,
        engine
    )


    # ==================================================
    # 4. MONTHLY SALES
    # ==================================================

    monthly_query = """
        SELECT
            DATE_FORMAT(`Order Date`, '%%Y-%%m') AS Month,
            SUM(Sales) AS Sales
        FROM sales
        GROUP BY DATE_FORMAT(`Order Date`, '%%Y-%%m')
        ORDER BY Month
        """

    monthly_df = pd.read_sql(
        monthly_query,
        engine
    )


    # ==================================================
    # 5. CREATE CATEGORY CHART
    # ==================================================

    category_chart = "sales_analysis_category.png"

    plt.figure(figsize=(7, 4))

    plt.pie(
        category_df["Sales"],
        labels=category_df["Category"],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Sales by Category")

    plt.tight_layout()

    plt.savefig(
        category_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 6. CREATE REGION CHART
    # ==================================================

    region_chart = "sales_analysis_region.png"

    plt.figure(figsize=(7, 4))

    plt.bar(
        region_df["Region"],
        region_df["Sales"]
    )

    plt.title("Sales by Region")

    plt.xlabel("Region")

    plt.ylabel("Sales")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        region_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 7. CREATE MONTHLY SALES CHART
    # ==================================================

    monthly_chart = "sales_analysis_monthly.png"

    plt.figure(figsize=(8, 4))

    plt.plot(
        monthly_df["Month"],
        monthly_df["Sales"],
        marker="o"
    )

    plt.title("Monthly Sales Trend")

    plt.xlabel("Month")

    plt.ylabel("Sales")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        monthly_chart,
        dpi=150
    )

    plt.close()


    # ==================================================
    # 8. CREATE PDF
    # ==================================================

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []


    # TITLE

    elements.append(
        Paragraph(
            "<b>Products Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated On : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )


    # ==================================================
    # KPI TABLE
    # ==================================================

    kpi_data = [

        [
            "Total Sales",
            "Total Profit",
            "Total Orders",
            "Average Discount"
        ],

        [
            f"₹{total_sales:,.2f}",
            f"₹{total_profit:,.2f}",
            f"{total_orders:,}",
            f"{avg_discount * 100:.2f}%"
        ]

    ]


    kpi_table = Table(
        kpi_data,
        colWidths=[
            1.3 * inch,
            1.3 * inch,
            1.3 * inch,
            1.3 * inch
        ]
    )


    kpi_table.setStyle(
        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("BOX", (0, 0), (-1, -1), 1, colors.grey),

            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ("TOPPADDING", (0, 0), (-1, -1), 8),

        ])
    )


    elements.append(kpi_table)

    elements.append(
        Spacer(1, 20)
    )


    # ==================================================
    # CHARTS
    # ==================================================

    elements.append(
        Paragraph(
            "<b>Sales by Category</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            category_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )

    elements.append(
        Spacer(1, 15)
    )


    elements.append(
        Paragraph(
            "<b>Sales by Region</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            region_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )

    elements.append(
        Spacer(1, 15)
    )


    elements.append(
        Paragraph(
            "<b>Monthly Sales Trend</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Image(
            monthly_chart,
            width=6.5 * inch,
            height=3.4 * inch
        )
    )


    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(elements)


    # ==================================================
    # DELETE TEMP CHARTS
    # ==================================================

    for file in [
        category_chart,
        region_chart,
        monthly_chart
    ]:

        if os.path.exists(file):
            os.remove(file)


    return FileResponse(
        pdf_file,
        filename="products_report.pdf",
        media_type="application/pdf"
    )