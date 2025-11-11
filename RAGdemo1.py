# import google.generativeai as genai
# import faiss
# import numpy as np

# # =============================
# # 1️⃣ Setup Gemini API key
# # =============================
# genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")  # 🔑 Replace with your Gemini API key

# # =============================
# # 2️⃣ Knowledge Base Documents
# # =============================
# documents = [
#     "Python is a high-level, interpreted programming language created by Guido van Rossum.",
#     "FAISS is a library for efficient similarity search and clustering of dense vectors.",
#     "Google Gemini is a large language model capable of reasoning, coding, and natural conversation.",
#     "RAG stands for Retrieval Augmented Generation. It combines information retrieval with LLMs."
# ]

# # =============================
# # 3️⃣ Create Embeddings
# # =============================
# embed_model = "models/embedding-001"

# embeddings = []
# for doc in documents:
#     result = genai.embed_content(model=embed_model, content=doc)
#     embeddings.append(result['embedding'])

# embeddings = np.array(embeddings).astype("float32")

# # =============================
# # 4️⃣ Build FAISS Index
# # =============================
# dimension = len(embeddings[0])
# index = faiss.IndexFlatL2(dimension)
# index.add(embeddings)

# # =============================
# # 5️⃣ Chat Loop
# # =============================
# chat_model = "gemini-2.5-flash"

# print("🤖 Chatbot ready! Type 'exit' to quit.\n")

# while True:
#     query = input("You: ")
#     if query.lower() == "exit":
#         print("Bot: Goodbye! 👋")
#         break

#     # Create embedding for the query
#     query_embedding = genai.embed_content(model=embed_model, content=query)['embedding']
#     query_embedding = np.array([query_embedding]).astype("float32")

#     # Search in FAISS for relevant document
#     D, I = index.search(query_embedding, k=1)
#     context = documents[I[0][0]]

#     # Use Gemini LLM to answer based on context
#     prompt = f"Context: {context}\nQuestion: {query}\nAnswer clearly using the given context."
#     response = genai.GenerativeModel(chat_model).generate_content(prompt)

#     print("Bot:", response.text)










import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 1️⃣ Gemini setup
genai.configure(api_key="AIzaSyBCSEzBz3lxXfj-5TO1arnuYAJAH5M4uNg")

# 2️⃣ Local embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    "Python is a high-level, interpreted programming language created by Guido van Rossum.",
    "FAISS is a library for efficient similarity search and clustering of dense vectors.",
    "Google Gemini is a large language model capable of reasoning, coding, and natural conversation.",
    "RAG stands for Retrieval Augmented Generation. It combines information retrieval with LLMs."
]

# 3️⃣ Create embeddings locally (free)
embeddings = embedder.encode(documents)
embeddings = np.array(embeddings).astype("float32")

# 4️⃣ Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 5️⃣ Chat loop
print("🤖 Chatbot ready! Type 'exit' to quit.\n")
chat_model = "gemini-2.5-flash"

while True:
    query = input("You: ")
    if query.lower() == "exit":
        print("Bot: Goodbye! 👋")
        break

    query_emb = embedder.encode([query]).astype("float32")
    D, I = index.search(query_emb, k=1)
    context = documents[I[0][0]]

    prompt = f"Context: {context}\nQuestion: {query}\nAnswer clearly using the given context."
    response = genai.GenerativeModel(chat_model).generate_content(prompt)
    print("Bot:", response.text)
