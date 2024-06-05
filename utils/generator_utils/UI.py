import re
import requests
import streamlit as st
from utils.generator_utils.AI_model import generate_test_cases,save_new_data
from utils.generator_utils.STPs import convert_output_to_excel,send_stp
from utils.generator_utils.User_Story import remove_formatting,remove_punctuation,remove_hyperlinks

# Function to extract issue data from JIRA and generate test cases
async def extract_issue(issue_key, accessible_resources, model, embedded_data):
    
    # Set up headers for API request
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Accept": "application/json"
    }

    # Iterate over accessible resources to find issue data
    for resource in accessible_resources:
        if "id" in resource:
            cloudid = resource["id"]  # Get the cloud ID from the resource
            api_endpoint = f"/rest/api/2/issue/{issue_key}"
            request_url = f"https://api.atlassian.com/ex/jira/{cloudid}{api_endpoint}"
            
            # Make a GET request to retrieve issue data
            response = requests.get(request_url, headers=headers)
            
            # Check if issue data is successfully retrieved
            if response.status_code == 200:
                user_story_data = response.json()
                description = user_story_data["fields"]["description"]  # Extract description field
                summary = user_story_data["fields"]["summary"]  # Extract summary field
                
                # Store issue details in session state
                st.session_state.issue_key = issue_key
                st.session_state.summary = summary
                st.session_state.description = remove_formatting(description)

                # Preprocess description for generating test cases
                description = remove_hyperlinks(description)
                description = remove_formatting(description)
                description = re.sub(r'\n\s*\n', '\n', description) #  Replace multiple newlines with a single new line

                # Generate test cases
                await generate_test_cases(model, description, embedded_data)

                # Update session state for UI elements
                st.session_state.modal_is_open = False
                st.session_state.display_user_story_button = True
                st.session_state.display_feedback_butttons = True
                st.session_state.modal2_is_open = False
                st.session_state.display_output_button = True
                st.session_state.modal3_is_open = False
                st.session_state.send_stp_button = True
                st.session_state.save_stp_button = True
                return
    
    # Display error message if issue fetch failed
    st.error("Failed to fetch issue. Please try again. Make sure to enter a valid issue key!")

    # Remove UI elements related to user story and feedback 
    st.session_state.pop("display_user_story_button", None)
    st.session_state.pop("display_feedback_butttons", None)
    st.session_state.pop("generated_output", None)

# Function to display Generator UI for entering user story when not logged in
async def display_user_story_entry_ui_when_not_logged_in(model,embedded_data):
    with st.container():
        user_story =st.chat_input("Enter a user story") # Input field for user story
        if user_story: 
            # Check if the input is not just whitespace
            if user_story.isspace():
                st.error("Please enter a valid input. The input cannot be empty or consist of only whitespace characters.")
            else:
                # Generate test cases based on the user story
                await generate_test_cases(model,user_story,embedded_data)

                 # Display user story and enable further actions if valid
                if "Please enter a valid user story" not in st.session_state.generated_output :
                    st.session_state.user_story = user_story
                    st.session_state.display_user_story_button=True

# Function to display Generator UI for entering input options when logged in
async def display_input_options_ui_when_logged_in(model,embedded_data):
    # Options for input: either an issue key or a user story
    options = ["Enter an issue key", "Enter a user story"]
    chosen_option = st.radio("Choose an option:", options)
    
    # Display the input field based on the chosen option
    if st.session_state.last_input_option != chosen_option:
    
    # Clear session state variables related to generated output and issue key
        st.session_state.pop("generated_output", None)
        st.session_state.pop("issue_key", None)
        st.session_state.pop("user_story", None)
    
    # Update last input option in session state
    st.session_state.last_input_option = chosen_option

    if chosen_option == "Enter an issue key":
        with st.container():
            issue_key = st.chat_input("Enter an issue key",)  # Input field for issue key
        text_user_story = None  
    else:
        with st.container():
            text_user_story = st.chat_input("Enter a user story") # Input field for user story
        issue_key = None 

    if issue_key:
        issue_key = issue_key.upper()   
        await extract_issue(issue_key, st.session_state.accessible_resources, model, embedded_data)
    elif text_user_story:
        if text_user_story.isspace(): # Check if user story is only whitespace
            st.error("Please enter a valid input. The input cannot be empty or consist of only whitespace characters.")
        else:
            await generate_test_cases(model,text_user_story,embedded_data)            
            if "Please enter a valid user story" not in st.session_state.generated_output :
                    st.session_state.user_story = text_user_story
                    st.session_state.display_user_story_button=True
                    st.session_state.display_feedback_butttons=True 

# Function to display generated output UI
async def display_generated_output_ui(model,embedded_data):
    
    # Display "Display user story" button if generated output exists
    if st.session_state.issue_key or st.session_state.user_story:
        if st.session_state.display_user_story_button:
            display_user_story_button = st.button("Display User Story",use_container_width=True)
            if display_user_story_button:
                # Open window 1 for displaying user story
                st.session_state.modal_is_open = True  

    # Get generated output
    output=st.session_state.generated_output  
    if "Please enter a valid user story" in output:
        st.session_state.pop("user_story", None)
        # Display warning message
        st.warning(output)
    else:
        # Display success message
        st.success("Output is available!")  
        display_output_button = st.button("Display Generrated Test Cases",use_container_width=True,type="primary")
        if display_output_button:
            # Open window 2 for displaying generated test cases
            st.session_state.modal2_is_open = True
        if "issue_key" in st.session_state and st.session_state.issue_key:
            issue_key = st.session_state.issue_key
            file_name = f"{issue_key}.xlsx"
        else:
            issue_key = ""
            file_name = "STP.xlsx"  
        col1, col2 = st.columns([1, 1]) 
        with col1:
            send_stp_buton=st.button("Send STP via Email",use_container_width=True)
            if send_stp_buton:
                # Open window 3 for sending email
                st.session_state.modal3_is_open = True
                send_button_clicked = st.session_state.get("send_button_clicked", False)
            
        with col2:
            # Display Button to save STP 
            save_stp_button = st.download_button("Download STP as an Excel file", convert_output_to_excel(st.session_state.generated_output), file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        
        st.write("\n\n")
        st.write("\n\n")
        
        if st.session_state.display_feedback_butttons:  
            if not st.session_state.is_feedback:
                col1, col2, col3 = st.columns([7, 2, 2])
                with col1:
                    # Display feedback prompt
                    st.write("Do you like this generated output? Give us your feedback!")

                with col2:
                    # Thumbs up button
                    if st.button(":thumbsup: Like", use_container_width=True):
                        if st.session_state.issue_key:
                            user_story = st.session_state.description
                        elif st.session_state.user_story:
                            user_story = remove_punctuation(st.session_state.user_story)
                            user_story = remove_hyperlinks(st.session_state.user_story)
                            user_story = re.sub(r'\n\s*\n', '\n', user_story)

                        # save the genertaed output and the entred user story in the Stoty2STP.db and the embedded user-story to the embedded_userstories.npy
                        await save_new_data(model, user_story, output, embedded_data)
                        st.session_state.is_feedback = True 
                        st.rerun()
                        
                with col3:
                    # Thumbs down button
                    if st.button(":thumbsdown: Dislike", use_container_width=True):
                        st.session_state.is_feedback = True   
                        st.rerun()
            else:
                st.balloons()  # Show balloons animation
                st.markdown('<center><b><font size="+2">Thank you for your feedback! 😊</font></b></center>',unsafe_allow_html=True) # Display thank you message
                st.session_state.display_feedback_butttons=False  # Hide feedback buttons
                st.session_state.is_feedback = False 

# Function to display window 1 UI "Display User Story"
def display_window1(Modal):
    window1 = Modal(key="model1", title="User Story",   max_width=744 )  
    with window1.container():
        st.session_state.modal_is_open = False
        if st.session_state.issue_key: # If user entred an issue key
            # Add formatting to the user-story
            st.markdown(f"""<div style='text-align: center;'><h3><span style='color:#2E9694'>Issue_Key: {st.session_state.issue_key}</span></h3></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style='text-align: center;'><h4><span style='color:#233d4d'>{st.session_state.summary}</span></h4></div>""", unsafe_allow_html=True)
            st.markdown(st.session_state.description)
        elif st.session_state.user_story: # If user entred a user-story
            st.markdown(remove_punctuation(st.session_state.user_story))
        close_button1 = st.button("Close",type="primary",use_container_width=True,key="close1")
        if close_button1: # If close button is clicked
            st.rerun()  # Rerun the app to close modal

# Function to display window 2 UI "Display Generated Output"
def display_window2(Modal):
    window2 = Modal(key="model2", title="Generated Output")  
    with window2.container():
        st.session_state.modal2_is_open = False
        if st.session_state.generated_output: # Display only if generated output exists
            st.markdown(st.session_state.generated_output)  # Display generated output
        close_button2 = st.button("Close",type="primary",use_container_width=True,key="close2")
        if close_button2:  # If close button is clicked
            st.rerun()  # Rerun the app to close modal

# Function to display window 3 UI "Send STP via Email"
def display_window3(Modal):
    window3 = Modal(key="model3", title="Send STP via Email")
    if "email_list" not in st.session_state:
        st.session_state.email_list = None
    
    # Function to verify if the entred emails are valid
    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None 
    
    with window3.container():
        with st.form(key="email_form"):  # Create a form for email input
            email_list = st.text_area("Enter your email(s)", height=85)  # Text area for entering email addresses
            submit_button = st.form_submit_button("Send Email", type="secondary", use_container_width=False)  # Submit button for form
            
        if submit_button:  # If submit button is clicked
            st.session_state.email_list=email_list  # Save email list in session state
            if email_list:
                emails = re.split(r'[,;\s]+', email_list)  # Split email list by commas, semicolons, and whitespace
                emails = list(filter(None, set(emails)))   # Remove empty strings and duplicates
                # Validate all email addresses
                if not all(is_valid_email(email.strip()) for email in emails):
                    st.error("Please enter valid email address.")  # Display error message for invalid email
                else:
                    # Convert generated output to Excel file
                    excel_file = convert_output_to_excel(st.session_state.generated_output)
                    issue_key = st.session_state.get("issue_key", "")
                    if not issue_key:
                        issue_key = ""
                        file_name = "STP.xlsx"  # Default file name for Excel file
                    else:
                        file_name = f"{issue_key}.xlsx"  # File name with issue key
                            
                    subject = "STP  "+ issue_key   # Subject for email

                    # Send STP via email
                    if send_stp(issue_key, emails, excel_file, file_name, subject):
                        # Display success message
                        st.success("Email sent successfully!")
                        # Remove email list from session state
                        st.session_state.pop("email_list",None)
                    else:
                        # Display error message                        
                        st.error("Failed to send email. Please check your email configuration.")
            else:
                # Display error message if email list is empty
                st.error("Please enter email address before sending.")
        
        close_button3 = st.button("Close",type="primary",use_container_width=True,key="close3")
        if close_button3: # If close button is clicked
            st.session_state.modal3_is_open = False  # Close modal(window)
            st.rerun() # Rerun the app to close modal 

