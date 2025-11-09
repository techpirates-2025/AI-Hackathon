import streamlit as st
import google.generativeai as genai

# -----------------------------
# Configure Gemini API key here
# -----------------------------
GEN_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # <-- Replace this with your Gemini API key
genai.configure(api_key=GEN_API_KEY)

# -----------------------------
# Initialize session state
# -----------------------------
if 'messages' not in st.session_state:
    st.session_state['messages'] = []  # list of dicts: {"role": "user"/"assistant", "content": "..."}

# -----------------------------
# Function to get Gemini response
# -----------------------------
def get_gemini_response(messages, model="gemini-2.5-flash"):
    """Send chat history to Gemini and get assistant reply."""
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append({"role": "user", "parts": [msg["content"]]})
        elif msg["role"] == "assistant":
            history.append({"role": "model", "parts": [msg["content"]]})

    model_instance = genai.GenerativeModel(model)
    chat = model_instance.start_chat(history=history)
    last_user = messages[-1]["content"]
    response = chat.send_message(last_user)
    return response.text

# -----------------------------
# Page Layout
# -----------------------------
st.set_page_config(page_title="Chat bot", page_icon="💬", layout="wide")
st.title("💬 Chat bot")

# -----------------------------
# Chat display CSS
# -----------------------------
st.markdown("""
<style>
.chat-box { padding: 12px; border-radius: 10px; margin-bottom: 8px; max-width: 80%; }
.user { background-color: #DCF8C6; margin-left: auto; text-align: right; }
.assistant { background-color: #F1F0F0; margin-right: auto; text-align: left; }
.meta { color: #666; font-size: 12px; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Display chat history
# -----------------------------
for msg in st.session_state['messages']:
    role = msg['role']
    content = msg['content']
    if role == "user":
        st.markdown(f"<div class='chat-box user'><div class='meta'>You</div>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box assistant'><div class='meta'>Assistant</div>{content}</div>", unsafe_allow_html=True)

# -----------------------------
# User input form
# -----------------------------
with st.form(key='input_form', clear_on_submit=True):
    user_input = st.text_area("", placeholder="Type your message here...")
    submit = st.form_submit_button("Send")
    
    if submit and user_input.strip():
        # Add user message
        st.session_state['messages'].append({"role": "user", "content": user_input})
        
        # Get assistant reply
        try:
            reply = get_gemini_response(st.session_state['messages'])
        except Exception as e:
            reply = f"(Error: {e})"
        
        st.session_state['messages'].append({"role": "assistant", "content": reply})
        st.experimental_rerun()
