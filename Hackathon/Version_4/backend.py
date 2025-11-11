# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import pandas as pd
import urllib3
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import os
import requests
from typing import Optional

app = FastAPI(title="Inventory Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - USE YOUR ACTUAL API KEY
API_KEY = "sk-tJBQbuRlJbjBPTosfFN6PQ"
BASE_URL = "https://genailab.tcs.in"
MODEL = "azure_ai/genailab-maas-DeepSeek-V3-0324"
CSV_FILE = "inventory.csv"

# Request models
class ChatRequest(BaseModel):
    message: str
    store_id: Optional[str] = "str001"

class ChatResponse(BaseModel):
    response: str
    status: str

class InventoryResponse(BaseModel):
    data: list
    total_records: int

# Disable SSL warnings and configure client
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False
requests.get = session.get

# Cache dir for tokens
tiktoken_cache_dir = "./token"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
client = httpx.Client(verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global agent instance
agent = None

def initialize_agent():
    """Initialize the CSV agent"""
    llm = ChatOpenAI(
        base_url=BASE_URL,
        model=MODEL,
        api_key=API_KEY,
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
       - Prefer eco-friendly or "EcoChoice" alternatives whenever possible.
       - Suggest checking nearby stores using the nearest ZIP code for availability.
       - Always include a user-friendly follow-up like:
         "Would you like me to check nearby stores for availability using your ZIP code?"

    4. Keep your responses structured and conversational.
       - Use bullet points or small tables for clarity.
       - Never invent or assume unavailable product information.

    Your goal is to act as a smart, helpful, and environmentally-conscious retail assistant that helps users quickly find what they need.
    """
    
    agent = create_csv_agent(
        llm,
        CSV_FILE,
        verbose=False,
        allow_dangerous_code=True,
        agent_instructions=instruction
    )
    
    return agent

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    try:
        agent = initialize_agent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")

@app.get("/")
async def root():
    return {"message": "Inventory Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        if not request.message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # Format the query with store context
        formatted_query = f"I'm in store {request.store_id}. {request.message}"
        
        # Get response from agent
        response = agent.run(formatted_query)
        
        return ChatResponse(
            response=response,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory", response_model=InventoryResponse)
async def get_inventory():
    try:
        df = pd.read_csv(CSV_FILE)
        return InventoryResponse(
            data=df.head(50).to_dict('records'),  # Increased limit for better preview
            total_records=len(df)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)