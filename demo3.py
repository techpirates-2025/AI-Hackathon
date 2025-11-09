# app.py
import os
import pandas as pd
import streamlit as st
import google.generativeai as genai

# -----------------------------
# 🔐 STEP 1: Configure Gemini API key
# -----------------------------
# Option 1: Directly
# genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")

# Option 2: Using environment variable (recommended)
# genai.configure(api_key=os.environ.get("AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg"))


genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")


# -----------------------------
# 📂 STEP 2: Load dataset
# -----------------------------
file_path = r"sales_data.xlsx"
df = pd.read_excel(file_path)

# Normalize column names for easier matching
df.columns = [col.lower().replace(" ", "_") for col in df.columns]

# Lowercase string columns for case-insensitive matching
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].astype(str).str.lower().str.strip()

normalized_columns = list(df.columns)

# -----------------------------
# 🧠 STEP 3: Define query processing function
# -----------------------------
def process_query(prompt, df, model="gemini-2.5-flash"):
    """Generate pandas code, execute it, and return concise LLM explanation."""
    # Step 1: Ask LLM to generate pandas code
    instruction = f"""
You are a data assistant working with a pandas DataFrame named `df`.
Columns: {normalized_columns}

User question: "{prompt}"

Return a **single line of pandas code** to answer this question.
If the question is unrelated to data, return "TEXT_RESPONSE".
Do not include explanations or markdown.
"""
    llm_model = genai.GenerativeModel(model)
    code_line = llm_model.generate_content(instruction).text.strip().strip("`").replace("python", "").strip()

    # Step 2: Execute pandas code
    if "TEXT_RESPONSE" in code_line:
        return llm_model.generate_content(prompt).text

    try:
        result = eval(code_line)
        if hasattr(result, "to_string"):
            result_text = result.to_string()
        else:
            result_text = str(result)
    except Exception as e:
        result_text = f"(Error executing code: {e})"

    # Step 3: Ask LLM to summarize result concisely
    explain_prompt = f"""
You are a precise and concise data analyst.
User asked: "{prompt}".
The pandas result is: {result_text}.
Write a **short factual summary** (1–2 sentences) based only on the data.
Do NOT use words like 'you', 'I', or 'our'.
Focus only on numeric/categorical facts.
"""
    explanation = llm_model.generate_content(explain_prompt)
    return explanation.text

# -----------------------------
# 🖥️ STEP 4: Streamlit UI
# -----------------------------
st.set_page_config(page_title="Data Chatbot", page_icon="💬", layout="wide")
st.title("💬 Smart Data Chatbot")

# Initialize chat history in session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# CSS for chat boxes


# st.markdown("""
# <style>
# .chat-box { padding: 12px; border-radius: 10px; margin-bottom: 8px; max-width: 80%; }
# .user { background-color: #DCF8C6; margin-left: auto; text-align: right; }
# .assistant { background-color: #F1F0F0; margin-right: auto; text-align: left; }
# .meta { color: #666; font-size: 12px; margin-bottom: 4px; }
# </style>
# """, unsafe_allow_html=True)


# -----------------------------
# Chat display CSS (ChatGPT-style with high contrast)
# -----------------------------
st.markdown("""
<style>
/* Chat bubble style - same background, high contrast text */
.chat-box {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
    background-color: #E1E1E2;  /* light gray bubble */
    color: #000000;             /* dark text for contrast */
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* User messages - right aligned */
.user {
    margin-left: auto;
    text-align: right;
}

/* Assistant messages - left aligned */
.assistant {
    margin-right: auto;
    text-align: left;
}

/* Role label above bubble */
.meta {
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 4px;
    color: #333333;  /* dark label for readability */
}

/* Scrollable chat area */
.chat-container {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Display chat inside scrollable container
# -----------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state['messages']:
    role = msg['role']
    content = msg['content']
    if role == "user":
        st.markdown(f"<div class='chat-box user'><div class='meta'>You</div>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box assistant'><div class='meta'>Assistant</div>{content}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)







# Display chat history
for msg in st.session_state['messages']:
    role = msg['role']
    content = msg['content']
    if role == "user":
        st.markdown(f"<div class='chat-box user'><div class='meta'>You</div>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box assistant'><div class='meta'>Assistant</div>{content}</div>", unsafe_allow_html=True)

# User input form
with st.form(key='input_form', clear_on_submit=True):
    user_input = st.text_area("", placeholder="Type your message here...")
    submit = st.form_submit_button("Send")

    if submit and user_input.strip():
        # Save user message
        st.session_state['messages'].append({"role": "user", "content": user_input})

        # Get assistant reply using pandas + Gemini
        try:
            reply = process_query(user_input, df)
        except Exception as e:
            reply = f"(Error: {e})"

        # Save assistant reply
        st.session_state['messages'].append({"role": "assistant", "content": reply})
        st.experimental_rerun()
