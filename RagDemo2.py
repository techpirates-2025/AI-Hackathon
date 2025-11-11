import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os

# 1️⃣ Gemini setup
genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")  # Replace with your Gemini key

# 2️⃣ Load any Excel/CSV file
file_path = "sales_data.xlsx"  # 📁 Put your file in same folder

if file_path.endswith(".xlsx"):
    df = pd.read_excel(file_path)
elif file_path.endswith(".csv"):
    df = pd.read_csv(file_path)
else:
    raise ValueError("Unsupported file format. Please use .xlsx or .csv")

# 3️⃣ Convert each row into a text document dynamically
documents = []
for _, row in df.iterrows():
    text_parts = [f"{col}: {row[col]}" for col in df.columns]
    text = ", ".join(text_parts)
    documents.append(text)

# 4️⃣ Create local embeddings (free)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(documents)
embeddings = np.array(embeddings).astype("float32")

# 5️⃣ Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 6️⃣ Chat loop
print("🤖 Universal Chatbot ready! Type 'exit' to quit.\n")
chat_model = "gemini-2.5-flash"

while True:
    query = input("You: ")
    if query.lower() == "exit":
        print("Bot: Goodbye! 👋")
        break

    query_emb = embedder.encode([query]).astype("float32")
    D, I = index.search(query_emb, k=5)
    # print(I[0])
    context = "\n".join([documents[i] for i in I[0]])
    # context = I[0]
    print(context)

    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer clearly using only the context."
    model = genai.GenerativeModel(chat_model)
    response = model.generate_content(prompt)

    print("Bot:", response.text)
