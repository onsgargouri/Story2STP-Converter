import streamlit as st
import secrets
import requests
import time
import asyncio

# Function to redirect to a URL
def redirect(url):
    # Generates HTML code to perform an automatic redirection to the specified URL
    html_code = f'<meta http-equiv="refresh" content="0; URL={url}" />'
    # Allow URL redirection in Streamlit
    st.markdown(html_code, unsafe_allow_html=True)

# Function to generate a random state
def generate_random_state():
    # Uses the secrets module to generate a secure random string
    return secrets.token_urlsafe(32)

# Function to check if the access token has expired
def access_token_expired(expiration_time):
    # If no expiration time is provided, we assume the token has expired
    if expiration_time is None:
        return True
    current_time = time.time() # Get current time in seconds 
    return current_time >= expiration_time

# Function to refresh the access token
def refresh_access_token(os,refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "client_id": os.getenv("jira_client_id"),
        "client_secret": os.getenv("jira_client_secret"),
        "refresh_token": refresh_token
    }
    token_url = "https://auth.atlassian.com/oauth/token"
    try:
        # Makes a POST request to refresh the access token
        response = requests.post(token_url, json=payload)
        if response.status_code == 200: 
            # If the request is successful, extract authorization data from the response
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            expiration_period = data.get("expires_in")
            st.success("refreshed token")
            return access_token, refresh_token, expiration_period
        else:
            # Display an error message if the token refresh fails
            st.error("Error refreshing access token. Please log in again.")
            return None, None, None
    except Exception as e:
        # Handle any exceptions that occur during the request
        st.error(e)
        return None, None, None

# Function to handle authorization
def handle_authorization(os):
    if "code" in st.query_params:
        # Authorization code is present in query parameters
        code = st.query_params["code"]
        token_url = "https://auth.atlassian.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("jira_client_id"),
            "client_secret": os.getenv("jira_client_secret"),
            "code": code,
            "redirect_uri": "http://localhost:8501"  # Redirect URI after authorization
        }
        
        # Make a POST request to exchange the authorization code for an access token
        response = requests.post(token_url, json=payload)
        
        if response.status_code == 200:
            # If the request is successful, extract authorization data from the response
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            expiration_period = data.get("expires_in")

            # Save tokens and authorization status in session state
            st.session_state.is_authorized = True
            st.session_state.is_logged_in = True
            st.session_state.access_token = access_token
            st.session_state.refresh_token = refresh_token
            st.session_state.expiration_time = time.time() + expiration_period
            st.rerun() # Rerun the app to update the state

        elif st.session_state.just_logged_out:
            # If the user just logged out, pass without doing anything
            pass
        
    elif "error" in st.query_params:
            # Display an error message if there was an error during authorization
            st.error("Failed to authorize! Please try again.")
    
# Function to save user authentication data
async def save_auth_data(db_manager):
    try:
        random_state=st.session_state.cookies["random_state"]
        try:
            # Save user data to the database
            await db_manager.save_user_data(random_state, st.session_state.access_token, st.session_state.refresh_token,st.session_state.expiration_time)
            st.session_state.is_logged_in = True
        except:
            if "UNIQUE constraint failed: users.random_state" in str(e):
                # User is already logged in, update session state accordingly
                st.session_state.is_logged_in = True  
                st.session_state.is_authorized = False
                st.rerun()
            else:
                # Display an error message if there is an issue saving the user data
                st.error("Error saving the new authorized user data to the database")
                st.session_state.is_logged_in = False  
                st.rerun()
            
    except Exception as e:
            # Handle any exceptions that occur during the saving process
            if st.session_state.random_state is not None:
                st.session_state.is_logged_in = True
            st.error(e)

# Function to fetch user data from Jira API
def fetch_user_data(os,db_manager):
    profile_url = "https://api.atlassian.com/me" # URL to fetch user profile data
    resources_url = "https://api.atlassian.com/oauth/token/accessible-resources" # URL to fetch accessible resources
    access_token = st.session_state.access_token
    if access_token_expired(st.session_state.expiration_time):
        # Refresh the access token if it has expired
        access_token, refresh_token, expiration_period = refresh_access_token(os,st.session_state.refresh_token)
        if access_token:
                # Update session state with new tokens
                st.session_state.access_token = access_token
                st.session_state.refresh_token = refresh_token
                st.session_state.expiration_time = time.time() + expiration_period
                try:
                    random_state=st.session_state.cookies["random_state"]
                    # Update database with new tokens
                    asyncio.run(db_manager.update_user_tokens(random_state, access_token, refresh_token, st.session_state.expiration_time))
                except:
                    pass
                st.rerun()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Make a GET request to fetch user profile data
    response1 = requests.get(profile_url, headers=headers)
    if response1.status_code == 200:
        user_data = response1.json()
        name = user_data.get("name")
        # Display a welcome message with the user's name
        st.header(f"Welcome {name} 👋")
    else:
        # Display an error message if fetching user information fails
        st.error("Error retrieving user information.")
    
    # Make a GET request to fetch accessible resources
    response = requests.get(resources_url, headers=headers)
    if response.status_code == 200: 
        # Extract accessible resources from the response
        accessible_resources = response.json()
        st.session_state.accessible_resources=accessible_resources
    else:
        # Display an error message if fetching accessible resources fails
        st.error(f"Error:{response.status_code}")

