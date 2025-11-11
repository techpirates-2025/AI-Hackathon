import streamlit as st
import httpx
import urllib3
from langchain_openai import ChatOpenAI
import os
import requests
from langchain_experimental.agents.agent_toolkits import create_csv_agent

# Page configuration
st.set_page_config(
    page_title="Inventory Assistant",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None

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

@st.cache_resource
def initialize_agent():
    """Initialize the CSV agent with caching to avoid reinitialization"""
    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in",
        model="azure_ai/genailab-maas-DeepSeek-V3-0324",
        api_key="sk-tJBQbuRlJbjBPTosfFN6PQ",
        http_client=client,
    )
    
    file_path = "Dataset_200.csv"
    
    instruction = """
You are an AI-powered Retail Inventory Assistant. Your task is to handle product availability and location queries accurately based on SKU ID or product name. 
Always respond with clear, structured, and human-friendly answers.

Follow these exact rules:

------------------------------------------------------------
🔹 WHEN USER QUERY CONTAINS A SKU ID
------------------------------------------------------------
1. Search the product in the **store inventory** using the SKU ID and quantity (if mentioned).
   - If available in store → show product_id, product_name, SKU, location, aisle, and available quantity.
   - Example response:
     "Milk 1L (SKU: M1001) is available in Store STR001, Aisle A3, Location: Dairy Section."

2. If not available in the store, search in the **warehouse**.
   - If available in warehouse → show same product details and specify it’s in the warehouse.
   - Example response:
     "Milk 1L (SKU: M1001) is not available in store STR001, but it’s available in the warehouse (Location: WH-A2)."

3. If not available in both store and warehouse:
   - Check for **related size variants** or similar prd_id (e.g., if ‘Milk 1L’ not found, suggest ‘Milk 500ml’).
   - Example response:
     "Milk 1L is out of stock, but Milk 500ml is available in Store STR001, Aisle A3."

4. If none of the above are available:
   - Provide **alternative stores** where the same SKU/product is available (based on zipcode proximity).
   - Example response:
     "Milk 1L is not available in STR001 or its warehouse, but available in STR003 (Zip: 641023)."

5. If the product is unavailable in all locations:
   - Suggest **related or similar category products**.
   - Example response:
     "Milk 1L is not available anywhere nearby. Would you like to see similar products like Soy Milk or Almond Milk?"


------------------------------------------------------------
🔹 WHEN USER QUERY CONTAINS A PRODUCT NAME (no SKU ID)
------------------------------------------------------------
1. Search for the product name in the **store inventory**.
   - If available → list product_id, product_name, SKU, location, aisle, and quantity.
   - Example response:
     "Milk is available in Store STR001, Aisle A3, Location: Dairy Section."

2. If not in store, check the **warehouse**.
   - Example response:
     "Milk is not available in Store STR001, but available in the warehouse (Location: WH-A2)."

3. If not available in both store and warehouse:
   - Suggest **other available variants or pack sizes**.
   - Example response:
     "Milk 1L is unavailable, but Milk 500ml is in stock at Store STR001."

4. If completely unavailable:
   - Provide **alternative store details** where the product is available.
   - Example response:
     "Milk is unavailable in STR001 and its warehouse, but available in Store STR003 (Zip: 641023)."

5. If not available anywhere:
   - Suggest **related category products** or **similar names**.
   - Example response:
     "Milk is not available anywhere nearby. Would you like to see similar dairy products such as Buttermilk or Curd?"


------------------------------------------------------------
🔹 RESPONSE STYLE
------------------------------------------------------------
- Always mention **store ID, location, aisle**, and **quantity if available**.
- Be clear and conversational, e.g.:
  "Yes, I found Milk 1L in Store STR001 at Aisle A3."
  "Sorry, it’s not available in Store STR001, but it’s in the warehouse."
- If nothing is found, always offer to help with alternatives:
  "Would you like me to suggest similar products?"

------------------------------------------------------------
"""


    
    agent = create_csv_agent(
        llm,
        file_path,
        verbose=False,
        allow_dangerous_code=True,
        agent_instructions=instruction
    )
    
    return agent

def main():
    # Header
    st.title("🛒 Inventory Assistant")
    st.markdown("Ask me anything about product availability, locations, and recommendations!")
    
    # Sidebar for additional information
    with st.sidebar:
        st.header("Store Information")
        store_id = st.text_input("Store ID", value="str001", help="Enter your current store ID")
        st.markdown("---")
        st.header("Instructions")
        st.markdown("""
        - Ask about product availability
        - Check warehouse stock
        - Get product recommendations
        - Find nearby store locations
        """)
        
        # Display sample questions
        st.header("Sample Questions")
        sample_questions = [
            "Do you have apples in stock?",
            "Where can I find milk in this store?",
            "Check warehouse for orange availability",
            "What fruits do you recommend?",
            "Find bananas in nearby stores"
        ]
        
        for question in sample_questions:
            if st.button(question, key=question):
                st.session_state.user_input = question
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("Initializing inventory assistant..."):
            try:
                st.session_state.agent = initialize_agent()
                st.success("Agent initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing agent: {e}")
                return
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                st.write(answer)
            if i < len(st.session_state.chat_history) - 1:
                st.markdown("---")
    
    # User input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Ask your question:",
            key="user_input",
            placeholder="e.g., Do you have apples in stock at store str001?"
        )
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Process user input
    if send_button and user_input:
        # Add store context if not already included
        if "store" not in user_input.lower() and "str001" not in user_input:
            # user_input = f"I'm in store {store_id}. {user_input}"
            user_input = f"{user_input}"
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
        
        # Get agent response
        with st.spinner("Searching inventory..."):
            try:
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    response_placeholder.write("Thinking...")
                    
                    # Get response from agent
                    # response = st.session_state.agent.run(user_input)
                    response = st.session_state.agent.run(f"I'm in store {store_id}. {user_input}")
                    
                    # Display response
                    response_placeholder.write(response)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((user_input, response))
                    
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.session_state.chat_history.append((user_input, error_msg))
        
        # Rerun to update the display
        st.rerun()

    # Display CSV data preview
    # st.markdown("---")
    # st.header("Inventory Data Preview")
    # try:
    #     df = pd.read_csv("inventory.csv")
    #     st.dataframe(df.head(10), use_container_width=True)
    #     st.caption(f"Total records: {len(df)}")
    # except Exception as e:
    #     st.warning(f"Could not load inventory data: {e}")

if __name__ == "__main__":
    main()