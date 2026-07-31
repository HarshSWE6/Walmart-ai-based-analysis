import streamlit as st
import pandas as pd
from groq import Groq
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ----------------------------
# Configuration
# ----------------------------

GROQ_API_KEY = "YOUR_GROQ_API_KEY"

client = Groq(api_key=GROQ_API_KEY)

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="YOUR_DB_PASSWORD",
    host="127.0.0.1",
    port=3306,
    database="walmartsales"
)

engine = create_engine(url)

# ----------------------------
# Page
# ----------------------------

st.set_page_config(
    page_title="AI Walmart Sales Analytics",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 AI Walmart Sales Analytics")

st.caption("Ask questions in plain English and get SQL, results, and business insights.")

question = st.text_input(
    "Business Question",
    placeholder="Example: Top 5 stores by revenue"
)

if st.button("Ask AI", use_container_width=True):
    prompt = f"""
You are an expert MySQL developer.

Database: walmartsales

Table: walmart_sales

Use ONLY these columns exactly as written:

Store
Dept
Date
Weekly_Sales
IsHoliday
Temperature
Fuel_Price
MarkDown1
MarkDown2
MarkDown3
MarkDown4
MarkDown5
CPI
Unemployment
Type
Size
Year
Month
Month_Name
Quarter
Week

Rules:
1. Return ONLY SQL.
2. Never invent column names.
3. Always use Weekly_Sales (NOT Sales).
4. Use MySQL syntax only.

Question:
{question}
"""



    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    sql = response.choices[0].message.content
    sql = sql.replace("```sql","").replace("```","").strip()

    st.subheader("Generated SQL")
    st.code(sql,language="sql")

    try:

        df = pd.read_sql(text(sql),engine)

        st.subheader("Query Result")
        st.dataframe(df,use_container_width=True)

        if len(df.columns)==2:

            st.subheader("Visualization")

            st.bar_chart(df.set_index(df.columns[0]))

        insight_prompt=f"""
You are a Business Analyst.

Question:
{question}

SQL:
{sql}

Result:
{df.to_string(index=False)}

Provide:
1. Key Findings
2. Recommendation

Maximum 5 bullet points.
"""

        insight=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role":"user",
                    "content":insight_prompt
                }
            ]
        )

        st.subheader("Business Insights")

        st.success(insight.choices[0].message.content)

    except Exception as e:

        st.error(e)