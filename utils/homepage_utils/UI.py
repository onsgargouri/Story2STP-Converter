import streamlit as st
from utils.homepage_utils.Authentication import redirect,generate_random_state,fetch_user_data
from streamlit_extras.switch_page_button import switch_page

# Function to display login options
async def display_login_options(os,controller,cookies,db_manager):
        st.write("### Welcome👋")
        st.markdown("""
        Convert your user stories into test cases effortlessly with our AI-powered tool.  
        Whether you're extracting stories from Jira or entering them manually, we've got you covered.""")
        st.write("##### Get Started Now ! ")
        
        # Creating two columns for page layout
        col1, col2 = st.columns([2, 1])
        with col1:
            button1 = st.button("Login with Jira Account", type="primary", use_container_width=True)

        with col2:
            button2 = st.button("Proceed without login", type="secondary", use_container_width=True)

        # Handling "Login with Jira Account" button click
        if button1:
            random_state=st.session_state.cookies["random_state"]  # Get random_state from cookies
            if st.session_state.cookies["random_state"] is not None:
                user_data =await db_manager.get_user_data(random_state)
                if user_data: 
                    # User has already authorized the app  
                    st.session_state.is_authorized = False
                    st.session_state.is_logged_in = True
                    st.session_state.access_token = user_data[1]
                    st.session_state.refresh_token = user_data[2]
                    st.session_state.expiration_time=user_data[3]
                    st.rerun()  # Refresh the page to update the session state
                else:
                    # If user is authorizing the app for the first time
                    redirect_url = f"https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={os.getenv('jira_client_id')}&scope=read%3Ajira-work%20read%3Ajira-user%20offline_access%20read%3Ame&redirect_uri=http%3A%2F%2Flocalhost%3A8501&state={random_state}&response_type=code&prompt=consent"
                    redirect(redirect_url)
            else:
                # Generate a new random state if not available in cookies
                random_state = generate_random_state()
                st.session_state.random_state=random_state
                st.session_state.cookies["random_state"] = random_state
                st.session_state.update(cookies=cookies)
                try:
                    # Set the random_state cookie with a max age of 30 days (= 2592000 seconds)
                    controller.set('random_state', random_state, max_age=2592000, secure=True)
                except Exception as e:
                    st.error(e)
                redirect_url = f"https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={os.getenv('jira_client_id')}&scope=read%3Ajira-work%20read%3Ajira-user%20offline_access%20read%3Ame&redirect_uri=http%3A%2F%2Flocalhost%3A8501&state={random_state}&response_type=code&prompt=consent"
                redirect(redirect_url)

        # Handling "Proceed without login" button click
        if button2:
            # Switch to the Generator page
            switch_page("Generator")
            st.rerun()

# Function to display the user profile and additional options
async def display_user_profile(os,controller,db_manager):
        st.write("""   
                """) 
        
        # Fetch and display user data from Jira API
        fetch_user_data(os,db_manager)
        st.write("Get Started Now ! ")

        # Button to go to the Converter page
        button3 = st.button("Go to Converter", type="primary", use_container_width=True)
        if button3:
            st.switch_page("pages/Generator.py")

        # Button to log out
        button4 = st.button("Logout", type="secondary", use_container_width=True)
        if button4:
            try:
                # Retrieve the random_state from the cookies and delete user data from the database
                random_state=controller.get("random_state")
                await db_manager.delete_user_data(random_state)
            except Exception as e:
                    st.error("Error while Removing Authentication Data")
                    
            # Clear session state related to authorization and login
            st.session_state.pop("is_authorized", None)
            st.session_state.pop("is_logged_in", None)
            st.session_state.just_logged_out = True
            st.rerun()  # Refresh the page to update the session state