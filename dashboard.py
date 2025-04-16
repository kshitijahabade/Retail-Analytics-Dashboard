import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from urllib.parse import quote_plus

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")
# Title
st.title("📊 Retail Orders - Data Analytics Dashboard")
st.markdown("""
Welcome to the **Retail Analytics Dashboard**!  
This project gives deep insights into sales, products, regions, and profitability using:
- 📦 A Kaggle dataset (Retail Orders)
- 🐍 Python (Pandas, SQLAlchemy)
- 💾 MySQL for data storage
- 📊 Streamlit + Plotly for dashboards
""")

#Side bar navigation
option = st.sidebar.radio("📌 Select a Report Section", [
    "Top Products", 
    "Region-Wise Bestsellers", 
    "Month-over-Month Sales",
    "Best Month per Category", 
    "Top Growing Sub-Category"
])

# DB Connection
username = "root"
password = quote_plus("Kshitu@123")
host = "127.0.0.1"
port = "3306"
database = "mydb"
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

if option == "Top Products":
    st.header("🔝 Top 10 Highest Revenue Generating Products")
    df1 = pd.read_sql("""
        SELECT product_id, SUM(sale_price) AS sales
        FROM mytb
        GROUP BY product_id
        ORDER BY sales DESC
        LIMIT 10;
    """, con=engine)
    st.dataframe(df1)
    st.bar_chart(df1.set_index("product_id"))
    csv = df1.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Top Products CSV", csv, "top_10_products.csv", "text/csv")



elif option == "Region-Wise Bestsellers":
    st.header("🌍 Top 5 Selling Products in Each Region")
    df2 = pd.read_sql("""
        SELECT * FROM (
            SELECT region, product_id, SUM(sale_price) AS total_sales,
                   RANK() OVER (PARTITION BY region ORDER BY SUM(sale_price) DESC) AS sales_rank
            FROM mytb
            GROUP BY region, product_id
        ) AS ranked_sales
        WHERE sales_rank <= 5
    """, con=engine)
    st.dataframe(df2)
    fig = px.bar(df2, x="product_id", y="total_sales", color="region", barmode="group")
    st.plotly_chart(fig)
    csv = df2.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Region-Wise Bestsellers CSV", csv, "Region-Wise Bestsellers.csv", "text/csv")


elif option == "Month-over-Month Sales":
    st.header("📈 Month-over-Month Sales Growth (2022 vs 2023)")
    df3 = pd.read_sql("""
        SELECT 
            MONTH(order_date) AS month_number,
            MONTHNAME(MAX(order_date)) AS month_name,
            SUM(CASE WHEN YEAR(order_date) = 2022 THEN sale_price ELSE 0 END) AS sales_2022,
            SUM(CASE WHEN YEAR(order_date) = 2023 THEN sale_price ELSE 0 END) AS sales_2023
        FROM mytb
        WHERE YEAR(order_date) IN (2022, 2023)
        GROUP BY MONTH(order_date)
        ORDER BY month_number
    """, con=engine)
    st.dataframe(df3)
    st.line_chart(df3.set_index("month_name")[["sales_2022", "sales_2023"]])
    csv = df3.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Month-over-Month Sales CSV", csv, "Month-over-Month Sales.csv", "text/csv")


elif option == "Best Month per Category":
    st.header("🏆 Highest Sales Month for Each Category")
    df4 = pd.read_sql("""
    SELECT 
        category,
        month_name,
        total_sales
    FROM (
        SELECT 
            category,
            DATE_FORMAT(order_date, '%%Y-%%m') AS month,
            MONTHNAME(MAX(order_date)) AS month_name,
            SUM(sale_price) AS total_sales,
            RANK() OVER (PARTITION BY category ORDER BY SUM(sale_price) DESC) AS sales_rank
        FROM mytb
        GROUP BY category, month
    ) AS ranked_sales
    WHERE sales_rank = 1;
    """, con=engine)


    st.dataframe(df4)

    csv = df4.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Best Month per Category CSV", csv, "Best Month per Category.csv", "text/csv")


elif option == "Top Growing Sub-Category":
    st.header("🚀 Sub-Category with Highest Profit Growth (2023 vs 2022)")
    df5 = pd.read_sql("""
        SELECT sub_category,
               SUM(CASE WHEN YEAR(order_date) = 2022 THEN profit ELSE 0 END) AS profit_2022,
               SUM(CASE WHEN YEAR(order_date) = 2023 THEN profit ELSE 0 END) AS profit_2023,
               ROUND(((SUM(CASE WHEN YEAR(order_date) = 2023 THEN profit ELSE 0 END) -
                       SUM(CASE WHEN YEAR(order_date) = 2022 THEN profit ELSE 0 END)) /
                       NULLIF(SUM(CASE WHEN YEAR(order_date) = 2022 THEN profit ELSE 0 END), 0)
               ) * 100, 2) AS growth_percent
        FROM mytb
        GROUP BY sub_category
        ORDER BY growth_percent DESC
        LIMIT 1
    """, con=engine)
    st.dataframe(df5)
    csv = df5.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Top Growing Sub-Category CSV", csv, "Top Growing Sub-Category.csv", "text/csv")


st.markdown("---")
st.markdown("✅ *Project by Kshitija Habade - Final Year Data Analytics Project*")
