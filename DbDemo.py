# ==============================================================
# 🔹 Intelligent Data Chatbot with SQLite + Custom LLM Endpoint
# ==============================================================

import os
import sqlite3
import pandas as pd
import urllib3
from httpx import Client
from langchain_openai import ChatOpenAI

# ==============================================================
# 1️⃣ Basic Setup (SSL and Warnings)
# ==============================================================
urllib3.disable_warnings()  # Suppress SSL warnings
os.environ["CURL_CA_BUNDLE"] = ""  # Helps with internal SSL certificates

# ==============================================================
# 2️⃣ Custom HTTP Client + LLM Initialization
# ==============================================================
client = Client(verify=False, timeout=60.0)

llm = ChatOpenAI(
    base_url="https://genailab.tcs.in/v1",   # ✅ internal endpoint
    model="gemini-2.5-flash",                # ✅ hosted model name
    api_key="sk-SshF5PVHJX2hTcQMjoW0zw",                           # ✅ replace with your valid API key
    temperature=0.3,
    http_client=client
)

# ==============================================================
# 3️⃣ SQLite Database Setup
# ==============================================================
DB_PATH = "user_data.db"

def init_db():
    """Initialize empty SQLite database file."""
    conn = sqlite3.connect(DB_PATH)
    conn.close()

def store_file_in_db(file_path):
    """Reads user-uploaded file and stores it in SQLite."""
    ext = os.path.splitext(file_path)[1].lower()
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    conn = sqlite3.connect(DB_PATH)

    # Read supported file formats
    if ext in [".csv", ".txt"]:
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type (use CSV, Excel, or TXT).")

    # Store dataframe to SQLite
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ Stored file data into table '{table_name}'")
    return table_name

# ==============================================================
# 4️⃣ Generate SQL Query using LLM (Fixed version)
# ==============================================================
def generate_sql_query(question, table_name):
    """Generate SQL query from user question with known schema."""

    known_columns = [
        "Order ID",
        "Date",
        "Region",
        "Salesperson",
        "Product",
        "Category",
        "Quantity",
        "Unit Price",
        "Total Sale",
        "Customer Type",
        "Payment Mode",
        "Profit"
    ]

    schema_description = "\n".join([f"- {col}" for col in known_columns])

    prompt = f"""
    You are an expert SQL data analyst.

    The table name is '{table_name}'.
    Here are the exact column names available:
    {schema_description}

    Important rules:
    - Use the column names exactly as given (case-sensitive, use double quotes if needed).
    - Do NOT invent new columns.
    - The SQL dialect is SQLite.
    - Only return the SQL query (no markdown, no explanations).
    - The query should always start directly with SELECT, UPDATE, INSERT, or DELETE.
    - Do NOT add any prefixes like 'sql', 'ite', or numbers before the query.

    The user question is:
    "{question}"
    """

    response = llm.invoke(prompt)
    sql_query = (
        response.content.strip()
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    # ✅ Sanitize - ensure SQL starts properly
    for keyword in ["SELECT", "UPDATE", "INSERT", "DELETE"]:
        if keyword in sql_query.upper():
            sql_query = sql_query[sql_query.upper().find(keyword):]
            break

    return sql_query

# ==============================================================
# 5️⃣ Execute SQL and Summarize Results
# ==============================================================
def execute_sql_and_summarize(sql_query, question, table_name):
    """Run SQL, fetch data, and ask LLM to summarize."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql_query, conn)
    except Exception as e:
        return f"❌ SQL Execution Error: {e}"
    finally:
        conn.close()

    # Limit large outputs
    preview = df.head(10).to_markdown(index=False) if not df.empty else "No results found."

    # Ask LLM to summarize the result
    summary_prompt = f"""
    You ran this SQL query on table '{table_name}':

    {sql_query}

    The result (first few rows):

    {preview}

    Based on the above, answer the user's question in natural language:

    "{question}"
    """
    response = llm.invoke(summary_prompt)
    return response.content.strip()

# ==============================================================
# 6️⃣ Chatbot Flow
# ==============================================================
def chatbot_flow(file_path, user_question):
    # Step 1: Store uploaded data into SQLite
    table_name = store_file_in_db(file_path)

    # Step 2: Generate SQL query
    sql_query = generate_sql_query(user_question, table_name)
    print("\n🧠 Generated SQL Query:\n", sql_query)

    # Step 3: Execute SQL and summarize
    answer = execute_sql_and_summarize(sql_query, user_question, table_name)
    print("\n💬 Final Answer:\n", answer)

# ==============================================================
# 7️⃣ Run Example
# ==============================================================
if __name__ == "__main__":
    init_db()

    # Example file path (user can upload)
    file_path = "sales_data.xlsx"

    # Example natural language question
    question = "Who sold the most products overall?"

    chatbot_flow(file_path, question)
