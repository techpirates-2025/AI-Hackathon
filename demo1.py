import google.generativeai as genai
import pandas as pd

# manoj
# Configure Gemini API key
genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")

# Load dataset (Excel or CSV)
# file_path = input("Enter your dataset file path: ")
# file_path = "sales_data.xlsx"
file_path = "C:/Users/Manoj T/Desktop/AI/sales_data.xlsx"
if file_path.endswith(".xlsx"):
    df = pd.read_excel(file_path)
elif file_path.endswith(".csv"):
    df = pd.read_csv(file_path)
else:
    print("Unsupported file format.")
    exit()

print("\n✅ Data Loaded Successfully!\n")
print(df.head())

# Create a model instance
# model = genai.GenerativeModel("models/gemini-1.5-flash")

model = genai.GenerativeModel("gemini-2.0-flash")

print("\n🤖 Data Chatbot Ready! Type 'exit' to quit.\n")

# Chat loop
while True:
    question = input("You: ")
    if question.lower() == "exit":
        print("👋 Goodbye!")
        break
    
    # Combine question and dataset context
    prompt = f"You are a data analysis assistant. Based on this dataset:\n\n{df.head(20).to_string()}\n\nAnswer this question: {question}"
    
    response = model.generate_content(prompt)
    print("Gemini:", response.text)

