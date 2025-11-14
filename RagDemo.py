# # ==============================================================
# # 🔹 RAG Chatbot with FAISS + TF-IDF + Custom Endpoint LLM
# # ==============================================================

# from langchain_openai import ChatOpenAI
# from httpx import Client
# from sklearn.feature_extraction.text import TfidfVectorizer
# import faiss
# import numpy as np
# import pandas as pd
# import urllib3
# import os

# # ==============================================================
# # 1️⃣ Basic Setup (SSL and warnings)
# # ==============================================================
# urllib3.disable_warnings()  # Suppress SSL warnings
# os.environ["CURL_CA_BUNDLE"] = ""  # Helps with internal SSL certificates

# # ==============================================================
# # 2️⃣ Custom HTTP Client + LLM Initialization
# # ==============================================================
# # Create HTTP client for internal SSL endpoint
# client = Client(verify=False, timeout=60.0)

# # Initialize custom endpoint model
# llm = ChatOpenAI(
#     base_url="https://genailab.tcs.in/v1",   # ✅ ensure this matches your endpoint structure
#     model="gemini-2.5-flash",                # ✅ hosted model name
#     api_key="sk-SshF5PVHJX2hTcQMjoW0zw",    # ✅ replace with your valid API key
#     temperature=0.3,
#     http_client=client
# )

# # ==============================================================
# # 3️⃣ Load Data (CSV / Excel)
# # ==============================================================
# file_path = "sales_data.xlsx"  # change as needed
# if file_path.endswith(".xlsx"):
#     df = pd.read_excel(file_path)
# elif file_path.endswith(".csv"):
#     df = pd.read_csv(file_path)
# else:
#     raise ValueError("Unsupported file format. Please use .xlsx or .csv")

# # Convert each row to a textual document
# documents = [
#     ", ".join([f"{col}: {row[col]}" for col in df.columns])
#     for _, row in df.iterrows()
# ]

# # ==============================================================
# # 4️⃣ Create Embeddings (TF-IDF + FAISS)
# # ==============================================================
# print("🔍 Creating document embeddings...")

# vectorizer = TfidfVectorizer(max_features=512, ngram_range=(1, 2))
# embeddings = vectorizer.fit_transform(documents).toarray().astype("float32")

# dimension = embeddings.shape[1]
# index = faiss.IndexFlatL2(dimension)
# index.add(embeddings)

# print(f"✅ Indexed {len(documents)} documents ({dimension} dimensions)\n")

# # ==============================================================
# # 5️⃣ Chat Loop (Retrieval + Generation)
# # ==============================================================
# print("🤖 RAG Chatbot ready with Gemini 2.5 Flash (via genailab)! Type 'exit' to quit.\n")

# while True:
#     query = input("You: ")
#     if query.lower().strip() == "exit":
#         print("Bot: Goodbye 👋")
#         break

#     try:
#         # Step 1: Retrieve relevant docs
#         query_emb = vectorizer.transform([query]).toarray().astype("float32")
#         D, I = index.search(query_emb, k=5)
#         context = "\n".join([documents[i] for i in I[0]])

#         # Step 2: Prepare prompt
#         prompt = f"""
#         You are an intelligent data assistant.
#         Use the given context to answer the question accurately and clearly.
        
#         Context:
#         {context}
        
#         Question:
#         {query}
        
#         Answer:
#         """

#         # Step 3: Get response from LLM
#         response = llm.invoke(prompt)

#         print("\nBot:", response.content.strip(), "\n")

#     except Exception as e:
#         print("❌ Error calling LLM:", e)
#         print()














# # ==============================================================
# # 🔹 Streamlit UI for RAG Chatbot (FAISS + TF-IDF + Gemini 2.5 Flash)
# # ==============================================================

# import streamlit as st
# from langchain_openai import ChatOpenAI
# from httpx import Client
# from sklearn.feature_extraction.text import TfidfVectorizer
# import faiss
# import numpy as np
# import pandas as pd
# import urllib3
# import os

# # ==============================================================
# # 1️⃣ Basic Setup (SSL + Streamlit Config)
# # ==============================================================
# urllib3.disable_warnings()
# os.environ["CURL_CA_BUNDLE"] = ""

# st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")

# st.markdown("""
#     <h2 style='text-align:center;'>💬 RAG Chatbot powered by Gemini 2.5 Flash</h2>
#     <p style='text-align:center;color:gray;'>Ask questions about your data and get intelligent answers</p>
# """, unsafe_allow_html=True)

# # ==============================================================
# # 2️⃣ File Upload
# # ==============================================================
# uploaded_file = st.file_uploader("📁 Upload your CSV or Excel file", type=["csv", "xlsx"])

# if uploaded_file is not None:
#     # Read uploaded file
#     if uploaded_file.name.endswith(".xlsx"):
#         df = pd.read_excel(uploaded_file)
#     else:
#         df = pd.read_csv(uploaded_file)

#     st.success(f"✅ Loaded {uploaded_file.name} with {len(df)} rows and {len(df.columns)} columns")

#     # ==============================================================
#     # 3️⃣ TF-IDF + FAISS Setup
#     # ==============================================================
#     documents = [
#         ", ".join([f"{col}: {row[col]}" for col in df.columns])
#         for _, row in df.iterrows()
#     ]

#     st.write("🔍 Creating document embeddings...")
#     vectorizer = TfidfVectorizer(max_features=512, ngram_range=(1, 2))
#     embeddings = vectorizer.fit_transform(documents).toarray().astype("float32")

#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)
#     st.success(f"✅ Indexed {len(documents)} documents ({dimension} dimensions)")

#     # ==============================================================
#     # 4️⃣ LLM Setup (Gemini Endpoint)
#     # ==============================================================
#     client = Client(verify=False, timeout=60.0)
#     llm = ChatOpenAI(
#         base_url="https://genailab.tcs.in/v1",
#         model="gemini-2.5-flash",
#         api_key="sk-SshF5PVHJX2hTcQMjoW0zw",  # 🔒 Replace with your valid key
#         temperature=0.3,
#         http_client=client
#     )

#     # ==============================================================
#     # 5️⃣ Chat Interface
#     # ==============================================================
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     user_query = st.chat_input("💬 Ask your question...")

#     if user_query:
#         # Step 1: Retrieve relevant context
#         query_emb = vectorizer.transform([user_query]).toarray().astype("float32")
#         D, I = index.search(query_emb, k=5)
#         context = "\n".join([documents[i] for i in I[0]])

#         # Step 2: Prepare prompt
#         prompt = f"""
#         You are an intelligent data assistant.
#         Use the given context to answer the question accurately and clearly.

#         Context:
#         {context}

#         Question:
#         {user_query}

#         Answer:
#         """

#         # Step 3: Get LLM response
#         try:
#             response = llm.invoke(prompt)
#             bot_reply = response.content.strip()
#         except Exception as e:
#             bot_reply = f"❌ Error calling LLM: {e}"

#         # Save chat history
#         st.session_state.chat_history.append(("user", user_query))
#         st.session_state.chat_history.append(("bot", bot_reply))

#     # ==============================================================
#     # 6️⃣ Display Chat Messages
#     # ==============================================================
#     for role, msg in st.session_state.chat_history:
#         if role == "user":
#             st.chat_message("user").markdown(msg)
#         else:
#             st.chat_message("assistant").markdown(msg)

# else:
#     st.info("👆 Please upload a CSV or Excel file to begin chatting.")











# ==============================================================
# 💬 Streamlit RAG Chatbot with Gemini 2.5 Flash + ChatGPT UI
# ==============================================================

import streamlit as st
from langchain_openai import ChatOpenAI
from httpx import Client
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import pandas as pd
import numpy as np
import urllib3
import os

# ==============================================================
# 1️⃣ Basic Setup (SSL + Streamlit Config)
# ==============================================================
urllib3.disable_warnings()
os.environ["CURL_CA_BUNDLE"] = ""

st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")

# --- Custom ChatGPT-style CSS ---
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #e6e6e6;
    }
    .main {
        background-color: #0e1117;
    }
    div.stChatMessage {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        max-width: 85%;
        line-height: 1.5;
    }
    div[data-testid="stChatMessage-user"] {
        background-color: #004d99;
        color: white;
        align-self: flex-end;
        margin-left: auto;
    }
    div[data-testid="stChatMessage-assistant"] {
        background-color: #1e1e2f;
        color: #e6e6e6;
        border: 1px solid #2a2a40;
    }
    .stTextInput>div>div>input {
        background-color: #1e1e2f;
        color: white;
        border: 1px solid #2a2a40;
    }
    .stFileUploader label {
        color: #e6e6e6;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================
# 2️⃣ Title
# ==============================================================
st.markdown("""
    <h2 style='text-align:center; color:#7dd3fc;'>💬 RAG Chatbot</h2>
    <p style='text-align:center; color:gray;'>Powered by Gemini 2.5 Flash ⚡</p>
""", unsafe_allow_html=True)

# ==============================================================
# 3️⃣ File Upload
# ==============================================================
uploaded_file = st.file_uploader("📁 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded **{uploaded_file.name}** with {len(df)} rows and {len(df.columns)} columns")

    # ==============================================================
    # 4️⃣ TF-IDF + FAISS Setup
    # ==============================================================
    documents = [
        ", ".join([f"{col}: {row[col]}" for col in df.columns])
        for _, row in df.iterrows()
    ]

    vectorizer = TfidfVectorizer(max_features=512, ngram_range=(1, 2))
    embeddings = vectorizer.fit_transform(documents).toarray().astype("float32")
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # ==============================================================
    # 5️⃣ LLM Setup (Gemini via TCS Endpoint)
    # ==============================================================
    client = Client(verify=False, timeout=60.0)
    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in/v1",
        model="gemini-2.5-flash",
        api_key="sk-SshF5PVHJX2hTcQMjoW0zw",  # 🔒 Replace with your actual API key
        temperature=0.3,
        http_client=client
    )

    # ==============================================================
    # 6️⃣ Chat Interface
    # ==============================================================
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.chat_input("💬 Type your question...")

    if user_query:
        # Step 1: Retrieve context
        query_emb = vectorizer.transform([user_query]).toarray().astype("float32")
        D, I = index.search(query_emb, k=5)
        context = "\n".join([documents[i] for i in I[0]])

        # Step 2: Prompt
        prompt = f"""
        You are a smart data analyst assistant. Use the given context to answer clearly and logically.
        Always give final numerical or factual answers from the data.

        Context:
        {context}

        Question:
        {user_query}

        Answer:
        """

        try:
            response = llm.invoke(prompt)
            bot_reply = response.content.strip()
        except Exception as e:
            bot_reply = f"❌ Error: {e}"

        # Save chat messages
        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("assistant", bot_reply))

    # ==============================================================
    # 7️⃣ Display Chat History
    # ==============================================================
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

else:
    st.info("👆 Upload a CSV or Excel file to start chatting with your data.")
