import streamlit as st
import os
from dotenv import load_dotenv
import asyncio
from sentence_transformers import SentenceTransformer
from streamlit_cookies_controller import CookieController
from utils.Databases_manager import AuthenticationDBManager
from utils.homepage_utils.Authentication import handle_authorization,save_auth_data
from utils.homepage_utils.UI import display_login_options,display_user_profile

# Set Streamlit page configuration
st.set_page_config(
    page_title="Story2Stp",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Load environment variables
load_dotenv()

# Initialize cookie controller to manage cookies
controller = CookieController()

# Asynchronously load the SentenceTransformer model
async def load_model():
        model = await asyncio.to_thread(SentenceTransformer, 'paraphrase-MiniLM-L6-v2')
        return model

# Main asynchronous function
async def main():
    # Initialize Streamlit title   
    st.title("🤖 Story2Stp Converter ")
    st.write("\n\n\n")
        
    # Initialize database manager for authentication
    db_manager = AuthenticationDBManager()

    # Create users table if not exists
    await db_manager.create_users_table()
    
    # Load the SentenceTransformer model if not already loaded
    if 'model' not in st.session_state:
        model = await load_model()
        st.session_state.model = model

    # Manage cookies in the session state
    cookies = st.session_state.cookies
    if cookies is None:
        cookies = {}  
    if "random_state" not in cookies:
        try:
            cookies["random_state"] = controller.get("random_state")
        except:
            cookies["random_state"]=None
            st.rerun()
    
    # Initialize various session state variables if they do not exist
    if "random_state" not in st.session_state:
        st.session_state.random_state = None
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "is_authorized" not in st.session_state:
        st.session_state.is_authorized = False
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None
    if "expiration_time" not in st.session_state:
        st.session_state.expiration_time = None
    if "just_logged_out" not in st.session_state:
        st.session_state.just_logged_out = False
    
    
    # Display login options if the user is not logged in
    if not st.session_state.is_logged_in:
        await display_login_options(os,controller,cookies,db_manager)

    else:
        # Display the user profile and options if logged in
        await display_user_profile(os,controller,db_manager)
        
            
    # Handle authorization: Check if the user has already authorized this app to access his jira account 
    if not st.session_state.is_authorized:
        handle_authorization(os)
        
    else:
        # Save authorization data to the database
        await save_auth_data(db_manager)

    # Display a logout message if the user just logged out
    if st.session_state.just_logged_out :
        st.success("Successfully logged out.")
        st.session_state.just_logged_out = False

# Run the main function using asyncio
asyncio.run(main())
