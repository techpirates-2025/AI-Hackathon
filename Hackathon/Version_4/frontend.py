# frontend.py
import streamlit as st
import requests
import pandas as pd
import json

# Configuration
BACKEND_URL = "http://localhost:8000"  # FastAPI backend URL

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
    .status-healthy {
        color: #2ca02c;
        font-weight: bold;
    }
    .status-unhealthy {
        color: #ff7f0e;
        font-weight: bold;
    }
    .status-offline {
        color: #d62728;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = None
if 'backend_status' not in st.session_state:
    st.session_state.backend_status = "unknown"

def check_backend_status():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            st.session_state.backend_status = "healthy"
            return True
        else:
            st.session_state.backend_status = "unhealthy"
            return False
    except:
        st.session_state.backend_status = "offline"
        return False

def send_message_to_backend(message, store_id):
    """Send message to backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                'message': message,
                'store_id': store_id
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Backend error: {response.status_code}', 'status': 'error'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Connection error: {str(e)}', 'status': 'error'}

def load_inventory_data():
    """Load inventory data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/inventory", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
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
    
    # Check backend status
    backend_healthy = check_backend_status()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Backend status
        status_display = {
            "healthy": "🟢 HEALTHY",
            "unhealthy": "🟡 UNHEALTHY", 
            "offline": "🔴 OFFLINE",
            "unknown": "⚪ UNKNOWN"
        }
        status_class = {
            "healthy": "status-healthy",
            "unhealthy": "status-unhealthy", 
            "offline": "status-offline",
            "unknown": "status-offline"
        }
        
        st.markdown(f"**Backend Status:** <span class='{status_class[st.session_state.backend_status]}'>{status_display[st.session_state.backend_status]}</span>", unsafe_allow_html=True)
        
        if not backend_healthy:
            st.error("⚠️ Backend is unavailable. Please ensure the backend server is running on port 8000.")
        
        st.markdown("---")
        st.header("🏪 Store Information")
        store_id = st.text_input("Current Store ID", value="str001", 
                               help="Enter your current store ID for accurate inventory checks")
        
        st.markdown("---")
        st.header("📋 Quick Actions")
        
        if st.button("🔄 Refresh All Data", use_container_width=True):
            st.session_state.inventory_data = load_inventory_data()
            check_backend_status()
            st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.header("💡 Sample Questions")
        
        sample_questions = {
            "Product Availability": "Do you have apples in stock?",
            "Product Location": "Where can I find milk in this store?",
            "Warehouse Check": "Check warehouse for orange availability",
            "Recommendations": "What fruits do you recommend?",
            "Nearby Stores": "Find bananas in nearby stores",
            "Eco-friendly Options": "Show me eco-friendly beverage options",
            "Stock Levels": "What's the current stock of bread?",
            "Product Search": "Do you have organic products?"
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
        - Specify **store ID** for accurate results
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
            data = st.session_state.inventory_data
            if 'data' in data:
                df = pd.DataFrame(data['data'])
                
                # Basic statistics
                total_products = len(df)
                total_records = data.get('total_records', total_products)
                
                # Calculate additional stats if columns exist
                if 'store_id' in df.columns:
                    total_stores = df['store_id'].nunique()
                else:
                    total_stores = 'N/A'
                
                if 'location_type' in df.columns:
                    total_warehouses = len(df[df['location_type'] == 'Warehouse'])
                else:
                    total_warehouses = 'N/A'
                
                st.metric("Total Products", total_products)
                st.metric("Total Stores", total_stores)
                st.metric("Warehouses", total_warehouses)
                
                # Quick data preview
                with st.expander("📋 Quick Data Preview"):
                    st.dataframe(df.head(5), use_container_width=True)
                    st.caption(f"Showing 5 of {total_records} products")
            else:
                st.warning("No inventory data available")
        else:
            if st.button("📥 Load Inventory Data"):
                with st.spinner("Loading inventory data..."):
                    st.session_state.inventory_data = load_inventory_data()
                st.rerun()
        
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
            label_visibility="collapsed",
            disabled=not backend_healthy
        )
    with col2:
        send_button = st.button(
            "Send ➡️", 
            use_container_width=True, 
            type="primary",
            disabled=not backend_healthy or not user_input
        )
    
    # Clear input button
    if st.button("Clear Input", use_container_width=True):
        st.session_state.user_input = ""
        st.rerun()
    
    # Process user input
    if send_button and user_input and backend_healthy:
        # Display user message immediately
        with chat_container:
            display_chat_message("user", user_input)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("🔍 Searching inventory...")
                
                # Send to backend
                response_data = send_message_to_backend(user_input, store_id)
                
                # Display response
                if response_data.get('status') == 'success':
                    response_placeholder.write(response_data['response'])
                    st.session_state.chat_history.append(
                        (user_input, response_data['response'], False)
                    )
                else:
                    error_msg = response_data.get('error', 'Unknown error occurred')
                    response_placeholder.error(f"Error: {error_msg}")
                    st.session_state.chat_history.append(
                        (user_input, error_msg, True)
                    )
        
        # Clear input and rerun
        st.session_state.user_input = ""
        st.rerun()
    
    # Inventory data section (collapsible)
    with st.expander("📦 Full Inventory Data", expanded=False):
        if st.session_state.inventory_data is not None:
            data = st.session_state.inventory_data
            if 'data' in data:
                df = pd.DataFrame(data['data'])
                
                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    if 'location_type' in df.columns:
                        location_filter = st.selectbox(
                            "Filter by Location Type:",
                            ["All"] + list(df['location_type'].unique())
                        )
                    else:
                        location_filter = "All"
                
                with col2:
                    if 'store_id' in df.columns:
                        store_filter = st.selectbox(
                            "Filter by Store:",
                            ["All"] + list(df['store_id'].unique())
                        )
                    else:
                        store_filter = "All"
                
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
        else:
            st.info("Click 'Load Inventory Data' button to view inventory information")

if __name__ == "__main__":
    main()