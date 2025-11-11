import streamlit as st
import httpx
import pandas as pd
import urllib3
from langchain_openai import ChatOpenAI
import os
import requests
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import time

# Page configuration
st.set_page_config(
    page_title="Retail Inventory Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #ddd;
    }
    .user-message {
        background-color: #e6f3ff;
        border-left: 4px solid #1f77b4;
    }
    .assistant-message {
        background-color: #f0f8f0;
        border-left: 4px solid #2ca02c;
    }
    .error-message {
        background-color: #ffe6e6;
        border-left: 4px solid #d62728;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = None

# Initialize the agent
def initialize_agent():
    """Initialize the CSV agent with caching to avoid reinitialization"""
    
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

    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in",
        model="azure_ai/genailab-maas-DeepSeek-V3-0324",
        api_key="sk-tJBQbuRlJbjBPTosfFN6PQ",
        http_client=client,
    )
    
    file_path = "inventory.csv"
    instruction = """
You are an intelligent Retail Inventory Assistant that helps store staff and customers locate products quickly.

Follow these rules strictly:

1. First, search for the requested product in the **current store’s inventory**.
   - If available, show details such as product name, SKU, aisle/location, and quantity.

2. If the product is **not found in the store**, check the **warehouse inventory**.
   - If available in the warehouse, show product details and mention that it can be arranged from the warehouse.

3. If the product is **not available in both the store and warehouse**, search for the **same product in other nearby stores** based on the user’s zipcode.
   - List all stores where it’s available, including store ID, location, and zipcode.

4. If the product is **completely unavailable**, politely inform the user and **suggest similar or related products**.
   - Example: “This item isn’t currently available. Would you like me to recommend related products?”

5. Always respond in a **professional and conversational** tone that sounds helpful and concise.

Example behaviors:
- “Apple is not available in store STR001, but it is available in warehouse W01. Would you like me to reserve it?”
- “The product ‘Banana’ isn’t in store STR005 or its warehouse, but available in store STR007 (zip 641045).”
- “Mango isn’t available anywhere nearby. Would you like me to suggest similar fruits?”
"""

    # instruction = """
    # You are an AI-powered Retail Inventory Query Agent.

    # Your main objective is to assist users in finding accurate product and stock details across stores and warehouses.

    # Follow the rules below while responding to user queries:

    # 1. When a user asks for a product:
    #    - Check if the product exists in the store inventory.
    #    - If available, provide complete details:
    #      • Product Name
    #      • Product ID / SKU
    #      • Available Stock Quantity
    #      • Location Type (Store / Warehouse)
    #      • Store Number, Location, Zipcode, and Aisle/Section (if available)

    # 2. If the product is not available in the current store:
    #    - Check in the warehouse.
    #    - If available in the warehouse, provide those details.

    # 3. If the product is not available at all:
    #    - Recommend similar or related products. 
    #      Example: If the user asks for "apple" and it's unavailable, suggest another fruit.
    #    - Prefer eco-friendly or "EcoChoice" alternatives whenever possible.
    #    - Suggest checking nearby stores using the nearest ZIP code for availability.
    #    - Always include a user-friendly follow-up like:
    #      "Would you like me to check nearby stores for availability using your ZIP code?"

    # 4. Keep your responses structured and conversational.
    #    - Use bullet points or small tables for clarity.
    #    - Never invent or assume unavailable product information.

    # Your goal is to act as a smart, helpful, and environmentally-conscious retail assistant that helps users quickly find what they need.
    # """
    
    agent = create_csv_agent(
        llm,
        file_path,
        verbose=False,
        allow_dangerous_code=True,
        agent_instructions=instruction
    )
    
    return agent

def load_inventory_data():
    """Load and display inventory data"""
    try:
        df = pd.read_csv("inventory.csv")
        return df
    except Exception as e:
        st.error(f"Error loading inventory data: {e}")
        return None

def display_chat_message(role, content, is_error=False):
    """Display a chat message with appropriate styling"""
    if role == "user":
        css_class = "user-message"
        icon = "👤"
    else:
        css_class = "error-message" if is_error else "assistant-message"
        icon = "❌" if is_error else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {role.capitalize()}:</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🛒 Retail Inventory Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Your AI-powered assistant for product availability and store information")
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("🔄 Initializing inventory assistant..."):
            try:
                st.session_state.agent = initialize_agent()
                st.session_state.inventory_data = load_inventory_data()
                st.success("✅ Agent initialized successfully!")
            except Exception as e:
                st.error(f"❌ Error initializing agent: {e}")
                return
    
    # Sidebar
    with st.sidebar:
        st.header("🏪 Store Information")
        store_id = st.text_input("Current Store ID", value="str001", 
                               help="Enter your current store ID for accurate inventory checks")
        
        st.markdown("---")
        st.header("📋 Quick Actions")
        
        if st.button("🔄 Refresh Inventory Data", use_container_width=True):
            st.session_state.inventory_data = load_inventory_data()
            st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.header("💡 Sample Questions")
        
        sample_questions = {
            "Product Availability": "Do you have apples in stock at store str001?",
            "Product Location": "Where can I find milk in this store?",
            "Warehouse Check": "Check warehouse for orange availability",
            "Recommendations": "What fruits do you recommend?",
            "Nearby Stores": "Find bananas in nearby stores using zipcode 12345",
            "Eco-friendly Options": "Show me eco-friendly beverage options"
        }
        
        for category, question in sample_questions.items():
            if st.button(f"{question}", key=question, use_container_width=True):
                st.session_state.user_input = question
                st.rerun()
        
        st.markdown("---")
        st.header("ℹ️ Instructions")
        st.markdown("""
        - Ask about **product availability** in stores
        - Check **warehouse stock** levels
        - Get **product recommendations**
        - Find **nearby store locations**
        - Look for **eco-friendly alternatives**
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Conversation")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                for i, (question, answer, is_error) in enumerate(st.session_state.chat_history):
                    display_chat_message("user", question)
                    display_chat_message("assistant", answer, is_error)
                    
                    if i < len(st.session_state.chat_history) - 1:
                        st.markdown("---")
            else:
                st.info("💡 Start a conversation by asking about product availability or using the sample questions in the sidebar!")
    
    with col2:
        st.subheader("📊 Inventory Summary")
        
        if st.session_state.inventory_data is not None:
            df = st.session_state.inventory_data
            
            # Basic statistics
            total_products = len(df)
            total_stores = df['store_id'].nunique() if 'store_id' in df.columns else 'N/A'
            total_warehouses = df[df['location_type'] == 'Warehouse']['store_id'].nunique() if 'location_type' in df.columns else 'N/A'
            
            st.metric("Total Products", total_products)
            st.metric("Total Stores", total_stores)
            st.metric("Warehouses", total_warehouses)
            
            # Quick data preview
            with st.expander("📋 Quick Data Preview"):
                st.dataframe(df.head(5), use_container_width=True)
                st.caption(f"Showing 5 of {len(df)} products")
        
        # Quick tips
        st.markdown("---")
        st.subheader("🚀 Quick Tips")
        st.markdown("""
        - **Be specific** with product names
        - **Mention store ID** for accurate results  
        - **Ask for alternatives** if unavailable
        - **Provide zipcode** for nearby store search
        """)
    
    # User input section
    st.markdown("---")
    st.subheader("💭 Ask a Question")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Enter your question:",
            key="user_input",
            placeholder="e.g., Do you have organic apples in store str001?",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send ➡️", use_container_width=True, type="primary")
    
    # Process user input
    if send_button and user_input:
        # Add store context if not already included
        formatted_query = user_input
        if "store" not in user_input.lower() and "str001" not in user_input:
            formatted_query = f"I'm in store {store_id}. {user_input}"
        
        # Display user message immediately
        with chat_container:
            display_chat_message("user", user_input)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("🔍 Searching inventory...")
                
                # Get agent response
                try:
                    start_time = time.time()
                    response = st.session_state.agent.run(formatted_query)
                    response_time = time.time() - start_time
                    
                    # Display response with formatting
                    formatted_response = f"{response}\n\n---\n*Response time: {response_time:.2f}s*"
                    response_placeholder.write(formatted_response)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((user_input, response, False))
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error while searching: {str(e)}"
                    response_placeholder.error(error_msg)
                    st.session_state.chat_history.append((user_input, error_msg, True))
        
        # Clear input and rerun
        st.session_state.user_input = ""
        st.rerun()
    
    # Inventory data section (collapsible)
    with st.expander("📦 Full Inventory Data", expanded=False):
        if st.session_state.inventory_data is not None:
            df = st.session_state.inventory_data
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                location_filter = st.selectbox(
                    "Filter by Location Type:",
                    ["All"] + list(df['location_type'].unique()) if 'location_type' in df.columns else ["All"]
                )
            with col2:
                store_filter = st.selectbox(
                    "Filter by Store:",
                    ["All"] + list(df['store_id'].unique()) if 'store_id' in df.columns else ["All"]
                )
            
            # Apply filters
            filtered_df = df.copy()
            if location_filter != "All" and 'location_type' in df.columns:
                filtered_df = filtered_df[filtered_df['location_type'] == location_filter]
            if store_filter != "All" and 'store_id' in df.columns:
                filtered_df = filtered_df[filtered_df['store_id'] == store_filter]
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export option
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv,
                file_name="filtered_inventory.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No inventory data available")

if __name__ == "__main__":
    main()