
import pandas as pd
import google.generativeai as genai

# ==============================
# 🔐 STEP 1: Configure Gemini
# ==============================
genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")
model = genai.GenerativeModel("gemini-2.5-flash")

# ==============================
# 📂 STEP 2: Load the dataset
# ==============================
file_path = r"C:\Users\Manoj T\Desktop\AI\sales_data.xlsx"
df = pd.read_excel(file_path)
print("✅ Data Loaded Successfully!\n")

# Normalize column names for flexible queries
df.columns = [col.lower().replace(" ", "_") for col in df.columns]
normalized_columns = list(df.columns)
print(f"📋 Normalized Columns: {normalized_columns}\n")

# ==============================
# 🧠 STEP 3: Start Interactive Chat
# ==============================
chat_history = []

print("🤖 Smart Data Chatbot Ready! Type 'exit' to quit.\n")

while True:
    prompt = input("You: ").strip()
    if prompt.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # Save user message
    chat_history.append(f"User: {prompt}")

    # Build LLM instruction with context memory
    context = "\n".join(chat_history[-5:])  # last few turns only
    instruction = f"""
You are an intelligent Python data assistant.
The user is asking questions about a pandas DataFrame named `df`.
The DataFrame has these columns: {normalized_columns}.

Conversation context:
{context}

Your task:
Generate ONE valid pandas code line to answer the user's latest query: "{prompt}"

Rules:
- Return only the Python code (no text or markdown)
- Prefer methods like value_counts(), groupby(), sum(), mean(), unique(), shape, etc.
- Use df for all operations
- If the query is unrelated to data, say "TEXT_RESPONSE"
    """

    try:
        # Ask LLM to generate pandas code
        llm_response = model.generate_content(instruction)
        code_line = llm_response.text.strip().strip("`").replace("python", "").strip()
        print(f"💻 Generated pandas code: {code_line}")

        # Evaluate the generated code safely
        if "TEXT_RESPONSE" in code_line:
            raise ValueError("Non-data question detected.")
        result = eval(code_line)

        # Display result
        print("📊 Result:\n", result, "\n")

        # Save result to chat history (partial for brevity)
        chat_history.append(f"Bot: Executed {code_line} -> {str(result)[:200]}")

    except Exception as e:
        print("⚠️ Error executing code:", e)
        # If pandas fails, fall back to LLM text answer
        try:
            response = model.generate_content(f"{context}\nUser: {prompt}")
            print("Gemini:", response.text, "\n")
            chat_history.append(f"Bot: {response.text}")
        except Exception as err:
            print("❌ LLM Error:", err)
