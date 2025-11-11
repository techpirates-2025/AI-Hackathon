# frontend.py
import streamlit as st
import requests
import pandas as pd
import time

# Configuration
BACKEND_URL = "http://localhost:8000"  # FastAPI default port

# Page configuration
st.set_page_config(
    page_title="Inventory Assistant",
    page_icon="🛒",
    layout="wide"
)

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
            }
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
    """Display a chat message"""
    with st.chat_message(role):
        if is_error:
            st.error(content)
        else:
            st.write(content)

def main():
    # Header
    st.title("🛒 Inventory Assistant")
    st.markdown("Ask me anything about product availability, locations, and recommendations!")
    
    # Check backend status
    backend_healthy = check_backend_status()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Backend status
        status_color = {
            "healthy": "🟢",
            "unhealthy": "🟡", 
            "offline": "🔴",
            "unknown": "⚪"
        }
        st.write(f"Backend Status: {status_color[st.session_state.backend_status]} {st.session_state.backend_status.upper()}")
        
        if not backend_healthy:
            st.error("Backend is unavailable. Please ensure the backend server is running.")
        
        st.markdown("---")
        st.header("🏪 Store Information")
        store_id = st.text_input("Store ID", value="str001", help="Enter your current store ID")
        
        st.markdown("---")
        st.header("📋 Instructions")
        st.markdown("""
        - Ask about product availability
        - Check warehouse stock  
        - Get product recommendations
        - Find nearby store locations
        """)
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "Do you have apples in stock?",
            "Where can I find milk in this store?",
            "Check warehouse for orange availability",
            "What fruits do you recommend?",
            "Find bananas in nearby stores"
        ]
        
        for question in sample_questions:
            if st.button(question, key=question, use_container_width=True):
                st.session_state.user_input = question
        
        st.markdown("---")
        
        # Quick actions
        st.header("⚡ Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.inventory_data = load_inventory_data()
            check_backend_status()
            st.rerun()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, (question, answer, is_error) in enumerate(st.session_state.chat_history):
                display_chat_message("user", question)
                display_chat_message("assistant", answer, is_error)
                
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("---")
    
    with col2:
        st.subheader("📊 Data")
        # Inventory data preview
        if st.session_state.inventory_data:
            data = st.session_state.inventory_data
            st.metric("Total Records", data.get('total_records', 0))
            if st.button("View Full Data"):
                st.session_state.show_full_data = True
        else:
            if st.button("Load Inventory Data"):
                with st.spinner("Loading inventory data..."):
                    st.session_state.inventory_data = load_inventory_data()
                st.rerun()
    
    # User input
    st.markdown("---")
    user_input = st.text_input(
        "Ask your question:",
        key="user_input",
        placeholder="e.g., Do you have apples in stock?",
        disabled=not backend_healthy
    )
    
    col1, col2 = st.columns([5, 1])
    with col1:
        send_button = st.button(
            "Send Message", 
            use_container_width=True, 
            type="primary",
            disabled=not backend_healthy or not user_input
        )
    with col2:
        clear_input = st.button("Clear", use_container_width=True)
    
    if clear_input:
        st.session_state.user_input = ""
        st.rerun()
    
    # Process user input
    if send_button and user_input and backend_healthy:
        # Display user message immediately
        with chat_container:
            display_chat_message("user", user_input)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("🤔 Searching inventory...")
                
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
        
        st.rerun()
    
    # Full inventory data display
    if st.session_state.get('show_full_data', False):
        st.markdown("---")
        st.header("📦 Full Inventory Data")
        
        if st.session_state.inventory_data:
            data = st.session_state.inventory_data
            if 'data' in data:
                df = pd.DataFrame(data['data'])
                st.dataframe(df, use_container_width=True)
                st.caption(f"Showing {len(df)} of {data['total_records']} total records")
            else:
                st.error("No data available")
        else:
            st.warning("No inventory data loaded")
        
        if st.button("Close Data View"):
            st.session_state.show_full_data = False
            st.rerun()

if __name__ == "__main__":
    main()