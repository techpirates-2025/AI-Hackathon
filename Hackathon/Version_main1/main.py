import streamlit as st
import httpx
import pandas as pd
import urllib3
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import requests
from langchain_experimental.agents.agent_toolkits import create_csv_agent

# =======================
# INITIAL CONFIGURATION
# =======================
st.set_page_config(page_title="🛒 AI Retail Inventory Query Agent", layout="wide")

# Load environment variables
load_dotenv()

# Disable SSL verification warnings
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False
requests.get = session.get

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cache directory for tokens
tiktoken_cache_dir = "./token"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

# HTTP client
client = httpx.Client(verify=False)

# =======================
# STREAMLIT UI
# =======================
st.title("🧠 AI-Powered Retail Inventory Query Agent")
st.write("Ask me about product availability, stock levels, or location in the store or warehouse!")

# Upload CSV (default fallback file)
uploaded_file = st.file_uploader("📂 Upload your inventory CSV file", type=["csv"])
if uploaded_file is not None:
    file_path = "uploaded_inventory.csv"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
else:
    file_path = "inventory.csv"  # Default CSV in working directory

# =======================
# LLM CONFIGURATION
# =======================
llm = ChatOpenAI(
    base_url="https://genailab.tcs.in",
    model="azure_ai/genailab-maas-DeepSeek-V3-0324",
    api_key="sk-tJBQbuRlJbjBPTosfFN6PQ",  # TODO: replace with environment var in prod
    http_client=client,
)

instruction = """
You are an AI-powered Retail Inventory Query Agent.

Your main objective is to assist users in finding accurate product and stock details across stores and warehouses.

Follow the rules below while responding to user queries:

1. When a user asks for a product:
   - Check if the product exists in the store inventory.
   - If available, provide complete details:
     • Product Name
     • Product ID / SKU
     • Available Stock Quantity
     • Location Type (Store / Warehouse)
     • Store Number, Location, Zipcode, and Aisle/Section (if available)

2. If the product is not available in the current store:
   - Check in the warehouse.
   - If available in the warehouse, provide those details.

3. If the product is not available at all:
   - Recommend similar or related products. 
     Example: If the user asks for "apple" and it's unavailable, suggest another fruit.
   - Prefer eco-friendly or “EcoChoice” alternatives whenever possible.
   - Suggest checking nearby stores using the nearest ZIP code for availability.
   - Always include a user-friendly follow-up like:
     “Would you like me to check nearby stores for availability using your ZIP code?”

4. Keep your responses structured and conversational.
   - Use bullet points or small tables for clarity.
   - Never invent or assume unavailable product information.

Your goal is to act as a smart, helpful, and environmentally-conscious retail assistant that helps users quickly find what they need.
"""

# =======================
# CREATE AGENT
# =======================
@st.cache_resource
def create_agent():
    return create_csv_agent(
        llm,
        file_path,
        verbose=False,
        allow_dangerous_code=True,
        agent_instructions=instruction
    )

agent = create_agent()

# =======================
# CHAT INTERFACE
# =======================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_query = st.text_input("💬 Ask about a product (e.g., 'I’m in store str001, I want to buy apple.')")

if st.button("Search"):
    if user_query:
        with st.spinner("🔍 Searching inventory..."):
            try:
                response = agent.run(user_query)
                st.session_state.chat_history.append(("User", user_query))
                st.session_state.chat_history.append(("Assistant", response))
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.subheader("🧾 Conversation History")
    for role, text in st.session_state.chat_history:
        if role == "User":
            st.markdown(f"**🧍‍♂️ You:** {text}")
        else:
            st.markdown(f"**🤖 Agent:** {text}")

# =======================
# DATA PREVIEW
# =======================
with st.expander("📊 View Inventory Data"):
    try:
        df = pd.read_csv(file_path)
        st.dataframe(df)
    except Exception as e:
        st.warning("Unable to read CSV file. Please upload a valid inventory dataset.")

