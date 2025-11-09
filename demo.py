import google.generativeai as genai

# Step 1: Configure your Gemini API key
genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")

# Step 2: Choose the AI model
model = genai.GenerativeModel("gemini-2.5-flash")

print("🤖 Gemini Chatbot — type 'exit' or 'quit' to stop.\n")


history = []
# Step 3: Keep asking for input in a loop
while True:
    prompt = input("You: ")
    
    # If user wants to exit
    if prompt.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break
    
    history.append({"role": "user", "parts": [prompt]})
    # Step 4: Send the prompt to Gemini and get response
    try:
        response = model.generate_content(history)
        print("Gemini:", response.text)
    
        history.append({"role": "model", "parts": [response.text]})

    except Exception as e:
        print("⚠️ Error:", e)
