import streamlit as st
import httpx
import pandas as pd
import urllib3
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from google.protobuf import descriptor_pb2
import os
import requests
from langchain_experimental.agents.agent_toolkits import create_csv_agent


api_key = load_dotenv()
API_KEY = os.getenv("sk-owOPRkEt3sfNOqOMB1wGyg")

requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False
requests.get = session.get

# Cache dir for tokens
tiktoken_cache_dir = "./token"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
client = httpx.Client(verify=False)
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


llm = ChatOpenAI(
    base_url="https://genailab.tcs.in",
    model="azure_ai/genailab-maas-DeepSeek-V3-0324",
    api_key="sk-tJBQbuRlJbjBPTosfFN6PQ",  # Use environment variables in prod!
    http_client=client,
)


file_path = "inventory.csv"

# instruction = """
# - if the product is not available at all recommend similar product example if a user ask for fruit tell if you want another fruit
#     - If product is not available check in warehouse
#     - even if the product is not available in warehouse tell the where the product is availble in nearby store based on zipcode
#     """

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


agent = create_csv_agent(
    llm,
    file_path,
    verbose = False,
    allow_dangerous_code = True,
    agent_instructions = instruction
)

ans = agent.run("Im in store str001 i want to buy apple do you know where it is")
print(ans)