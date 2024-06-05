import streamlit as st
from streamlit_modal import Modal
import numpy as np
import asyncio
import os
from dotenv import load_dotenv
from utils.Databases_manager import AuthenticationDBManager
from utils.homepage_utils.Authentication import fetch_user_data
from utils.generator_utils.UI import (
    display_input_options_ui_when_logged_in,
    display_user_story_entry_ui_when_not_logged_in,
    display_generated_output_ui,
    display_window1,
    display_window2,
    display_window3,
)

# Load environment variables
load_dotenv()

# Main asynchronous function for the Generatoo page
async def main():

    # Page setup
    st.page_link("Homepage.py", label="**Homepage** 🏠") # Link to the homepage
    st.title("Test Plan Generator")

    # Load the embedded data file and cache it to avoid reloading
    @st.cache_data()  
    def load_encoded_data():
        return np.load("data/embedded_userstories.npy")  # Load the embedded user stories data from a file
     # Load and store the embedded data
    embedded_data = load_encoded_data()
    
    # Load necessary objects from session state
    model = st.session_state.model  # Load the AI model from session state
    db_manager = AuthenticationDBManager()  # Create an instance of the AuthenticationDBManager

    # Asynchronously Connect to the database
    await db_manager.connect_to_database()

    # Initialize session state variables
    if "generated_output" not in st.session_state:
        st.session_state.generated_output = None
    if "last_input_option" not in st.session_state:
        st.session_state.last_input_option = None
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "is_feedback" not in st.session_state:
        st.session_state.is_feedback = False
    if "issue_key" not in st.session_state:
        st.session_state.issue_key = None
    if "user_story" not in st.session_state:
        st.session_state.user_story = None
    if "modal_is_open" not in st.session_state:
        st.session_state.modal_is_open = False
    if "display_user_story_button" not in st.session_state:
        st.session_state.display_user_story_button = False
    if "display_feedback_butttons" not in st.session_state:
        st.session_state.display_feedback_butttons=False
    if "modal2_is_open" not in st.session_state:
        st.session_state.modal2_is_open = False
    if "display_output_button" not in st.session_state:
        st.session_state.display_output_button = False
    if "modal3_is_open" not in st.session_state:
        st.session_state.modal3_is_open = False
    if "send_stp_button" not in st.session_state:
        st.session_state.send_stp_button = False
    if "save_stp_button" not in st.session_state:
        st.session_state.save_stp_button = False
    if "send_button_clicked" not in st.session_state:
        st.session_state.send_button_clicked = False

    # Check if the user is logged in
    if st.session_state.is_logged_in:
        fetch_user_data(os,db_manager)
        # Display input options UI when logged in
        await display_input_options_ui_when_logged_in(model,embedded_data)    
        
    else:
        # Display text user story entry UI when not logged in
        await display_user_story_entry_ui_when_not_logged_in(model,embedded_data)

    # Check if there is generated output             
    if hasattr(st.session_state, 'generated_output') and st.session_state.generated_output is not None:
        # Display the generated output UI
        await display_generated_output_ui(model,embedded_data)
    

    # Render window if the session state indicates it
    if st.session_state.modal_is_open:
        # Display window 1
        display_window1(Modal)
        
    if st.session_state.modal2_is_open:
        # Display window 2
        display_window2(Modal)

    if st.session_state.modal3_is_open:
        # Display window 3
        display_window3(Modal)  

# Run the main function until complete
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

