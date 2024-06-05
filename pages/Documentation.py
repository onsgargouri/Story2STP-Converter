import streamlit as st

# Link to the homepage
st.page_link("Homepage.py", label="**Homepage** 🏠")

# Page title and introduction
st.title("📘 Story2Stp Documentation 📘")
st.write("Welcome to Story2Stp🤖! This documentation will guide you through the various features of the web application and how to use them effectively. Follow these detailed steps to get the most out of your experience with Story2Stp.")

# Table of Contents
st.markdown("## Table of Contents")
st.markdown("I. [Introduction](#introduction)")
st.markdown("II. [Accessing the Application](#accessing-the-application)")
st.markdown("III. [Homepage Overview](#homepage-overview)")
st.markdown("    1. [Logging In](#logging-in)")
st.markdown("    2. [Logging Out](#logging-out)")
st.markdown("IV. [Generator Page](#generator-page)")
st.markdown("    1. [Unauthenticated Users](#unauthenticated-users)")
st.markdown("    2. [Authenticated Users](#authenticated-users)")
st.markdown("    3. [User Story Window](#user-story-window)")
st.markdown("    4. [Generated Output Window](#generated-output-window)")
st.markdown("    5. [Sending STP via Email](#sending-stp-via-email)")
st.markdown("    6. [Providing Feedback](#Providing-Feedback)")
st.markdown("V. [Troubleshooting](#troubleshooting)")

# Introduction
st.header("I. Introduction",anchor="introduction")
st.write("Story2Stp is a web application designed to help manual QA testers convert user stories into software test plans (STP) using AI technology. This documentation will guide you through the app’s functionalities and provide tips for a smooth user experience.")

# Accessing the Application
st.header("II. Accessing the Application",anchor="accessing-the-application")
st.write("To access Story2Stp, navigate to the web application URL in your preferred web browser. Ensure you have a stable internet connection for optimal performance.")

# Homepage Overview
st.header("III. Homepage Overview", anchor="homepage-overview")
st.write("- The homepage is the initial landing page of the application.")
st.write("- You can see links to log in, access the generator page, and view additional information.")
st.write("- You can also access different pages from the sidebar (click on '>' on the top left)")
# Logging In
st.subheader("1. Logging In", anchor="logging-in")
st.write("1. Click on the 'Login with Jira Account' button on the homepage.")
st.write("2. You will be redirected to the Jira login page where you need to enter your Jira credentials.")
st.image("doc_pictures/2.PNG", caption="Jira Login Redirection Page", width=300)
st.write("3. After entering your credentials, you will be directed to an authorization consent page.")
st.image("doc_pictures/3.PNG", caption="Authorization Consent Page", width=300)
st.write("4. Grant the necessary permissions for Story2Stp to access your Jira account. These permissions include access to user profile and issue data. You must explicitly grant or deny these permissions based on your prefrences.")
st.write("5. Upon successful authorization, you will be redirected back to the homepage. From here, you can proceed to the converter or log out.")

# Logging Out
st.subheader("2. Logging Out", anchor="logging-out")
st.write("1. To log out, click on the 'Log Out' button located on the homepage (after login).")
st.write("2. A confirmation message will display, indicating that you have successfully logged out.")
st.error("⚠️ **Please be aware that logging out will require you to reauthorize the app upon your next use. If you remain logged in, your authorization will persist across sessions. However, for security reasons, authorization will expire after 30 days.**")

st.header("IV. Generator Page", anchor="generator-page")
# Generator Page for Unauthenticated Users
st.subheader("1. Generator Page for Unauthenticated Users", anchor="unauthenticated-users")
st.write("- Users who choose to proceed without logging in will have limited functionality.")
st.image("doc_pictures/1.PNG", caption="Generator Page Unauthenticated", width=500)
st.write("- You can manually enter user stories into the input fields provided.")
# Entering User Stories Section
st.error("⚠️ When entering user stories, please try to make them clear and follow the format:\n **'As a [user], I want to [need] so that [goal].**\n This system is only for generating user stories, so please make sure to enter valid ones.\n Do not enter random text or greetings.")
# Generator Page for Authenticated Users
st.subheader("2. Generator Page for Authenticated Users",  anchor="authenticated-users")
st.write("1. After logging in, click on 'Go to Converter'.")
st.write("2. You have the option to either manually enter user stories or provide an issue key to extract user stories directly from your Jira account.")
st.image("doc_pictures/5.PNG", caption="Generator Page Authenticated", width=500)
st.write("3. Enter the required details and click on the 'Enter' keyboard button or on the icon '>'.")

# User Story Window
st.subheader("3. User Story Window",anchor="user-story-window")
st.write("- This window displays the user stories retrieved or entered.")

# Generated Output Window
st.subheader("4. Generated Output Window",  anchor="generated-output-window")
st.write("- After generating the output, this window shows the generated test plan from the AI model based on your inputs.")

# Sending STP via Email
st.subheader("5. Sending STP via Email", anchor="sending-stp-via-email")
st.write("1. To send the generated STP via email, click on the 'Send via Email' button.")
st.write("2. Enter the recipient’s email address. You can enter one or many email addresses.")
st.write("3. Click 'Send'.")
st.write("4. If the email format is incorrect, an error message will prompt you to correct it.")

# Providing Feedback
st.subheader("6. Providing Feedback", anchor="Providing-Feedback")
st.write("1. After reviewing the generated output, you can provide feedback on the generated output. This will avoid the AI model to improve continuously.")
st.image("doc_pictures/7.PNG", caption="Feedback Buttons", width=600)
st.write("2. Click the appropriate feedback button based on your satisfaction.")
st.write("3. A thank you message will appear after submitting your feedback.")

# Troubleshooting
st.header("V. Troubleshooting", anchor="troubleshooting")
st.write("- **Failed Authorization**: If authorization fails, retry logging in and and make sure to grant the necessary permissions.")
st.image("doc_pictures/4.png", caption="Failed Authorization", width=600)
st.write("- **Incorrect User Story Key**: Verify the user story key and re-enter it if an error message appears.")
st.image("doc_pictures/6.PNG", caption="Incorrect User Story Key", width=600)
st.write("- **Email Issues**: Ensure email addresses are correctly formatted to avoid input errors.")
st.image("doc_pictures/10.PNG", caption="Incorrect Email Address(es)", width=600)
st.write("- **Empty User Story**: Verify that the user story is not empty or containing whitespaces only.")
st.image("doc_pictures/11.PNG", caption="Empty User Story", width=600)
