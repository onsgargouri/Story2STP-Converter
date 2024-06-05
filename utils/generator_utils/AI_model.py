import google.generativeai as genai   # pip install google-generativeai
import numpy as np
import sqlite3
import re
import os
from dotenv import load_dotenv
from utils.Databases_manager import StorySTPDBManager
import streamlit as st

# Load environment variables
load_dotenv() 

# Configure the Google Generative AI library with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#Function to format output from the model 
    #This function is used only if the output is extracted from the databse and it do not follow the desired format)
def format_output(output):
     # Function to split the output string by test case
    def split_output_by_TestCase(output):
        return re.findall(r"Test Case \d+:.*?(?=Test Case \d+:|\Z)", output, re.DOTALL)

    # Function to extract text between two patterns
    def text_between_patterns(start_pattern, end_pattern, text):
        start_index = text.find(start_pattern) + len(start_pattern)
        end_index = text.find(end_pattern, start_index) if end_pattern else len(text)
        return text[start_index:end_index].strip()

    # Function to remove extra punctuation from the text
    def remove_extra_punctuation(text):
        return re.sub(r"^\s*:\s*", "", text, flags=re.MULTILINE)

    # Split the output into individual test cases
    test_cases = split_output_by_TestCase(output)

    # Initialize an empty string to store the formatted output
    formatted_output = ""

    # Loop through each identified test case
    for i, test_case in enumerate(test_cases, start=1):
        formatted_output += f"### Test Case: TC{i}\n"  # Add a heading for the test case with its sequential number 
        formatted_output += "###### Test Case Description:\n"
        formatted_output += text_between_patterns("Test Case Description:", "Preconditions", test_case) + "\n\n"  # Add a sub-heading for the test case description
        formatted_output += "###### Preconditions:\n"
        formatted_output += remove_extra_punctuation(text_between_patterns("Preconditions", "Steps", test_case)) + "\n\n"   # Add a sub-heading for the test case preconditions
        formatted_output += "###### Steps:\n"
        formatted_output += remove_extra_punctuation(text_between_patterns("Steps", "Expected Result", test_case)) + "\n\n" # Add a sub-heading for the test case steps
        formatted_output += "###### Expected Result:\n"
        formatted_output += remove_extra_punctuation(text_between_patterns("Expected Result", "", test_case)) + "\n\n"  # Add a sub-heading for the expected result of the test case
    return formatted_output

# Function to generate test cases for a user story using model 1 (For the First API Call).
def model1(input_text):
    # Set up the model configuration
    generation_config = {
    "temperature": 0.6,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 7000, 
    }

    # Set up the safety settings
    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    ]

    # Initialize the generative model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", 
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    # Define prompt instruction of model 1
    prompt_parts = [
    "You are a Quality Assurance (QA) team member. Given a user story, your task is to convert it into a structured paragraph containing multiple test cases. Each test case should include the following components:\n- Test Case: TC + A unique identifier for each test case, starting from 1 and incrementing by 1 for each subsequent test case.\n- Test Case Description: A brief description of the test case.\n- Preconditions: Any conditions or prerequisites that must be met before executing the test case.\n- Steps: The sequence of steps to be performed during the test case execution.\n- Expected Result: The expected outcome or result of the test case execution.\nGuidelines:\n- Wholeness: you must consider and cover all possible test cases related to the user story, including all possible test cases within each provided scenario.\n- Handling Non-User Story Inputs: if the input is a random statement, such as casual greetings, you must assign the output exactly as follows: \"Please enter a valid user story\"\n- Handling unclear user stories: if the input appears to describe a user's goal but lacks clarity, attempt to rephrase it as a proper user story and continue with test case generation.\n- Referencing: if the user story contains additional context denoted by (Reference), you should first generate test cases based on the user story. Then, you must leverage relevant information from the given reference to enhance the existing test cases contextually. Additionally, create as many additional test cases as possible, drawing inspiration from the test cases within the reference.\n- Formatting: Each test case should be formatted as follows:\n    - Write \"Test Case: TC+ID\" only once at the beginning.  Make sure to use markdown formatting(###) to make it a heading       \n    - Use markdown formatting(######) for the titles \"Test Case Description \\n\", \"Preconditions \", \"Steps\", and \"Expected Result \".  The headings must apply only to the phrases themselves and not to their content.\n    - Use bullet points (\"-\") for \"Preconditions\".\n    - Use numbered lists (\"1.\", \"2.\", etc.) for \"Steps\".",
    f"input: {input_text}",
    "output: ",
    ]
    max_retries = 3  # Maximum number of retries for generating content

    for attempt in range(max_retries):
        try:
            # Generate content using the model
            response = model.generate_content(prompt_parts) 
             # Extract the generated text
            ai_output = response.text
            if "Please enter a valid user story" not in ai_output:
                # Break the loop if valid output is generated
                break
            else:
                print("Invalid output:", ai_output)
        except ValueError as e:
            # Handle any errors during generation
            ai_output = "Error. Please try again!"
    return ai_output

# Function to generate test cases for a user story using model 2 (For the Second API Call).
def model2(input_text):
    if "Please enter a valid user story" in input_text:
        ai_output="Please enter a valid user story"
    else:

        # Set up the model configuration
        generation_config = {
        "temperature": 0.6,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 7000,
        }

        # Set up the safety settings
        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_LOW_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_LOW_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_LOW_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_LOW_AND_ABOVE"
        },
        ]

        # Initialize the generative model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro", 
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)
        
        # Define prompt instruction of model 1
        prompt_parts = [
        "You are a Quality Assurance (QA) team member. Given the described user story and the existing developed test cases, your task is to develop additional relevant test cases, by considering unmentioned situations, edge cases, and exceptional conditions. These test cases should aim to uncover potential weaknesses or vulnerabilities in the system's behavior and to ensure comprehensive test coverage.\nGuidelines:\n*Handling Non-User Story Inputs: If the input contains \"Please enter a user story\" or conveys a similar meaning, then you must assign the output \"Please enter a valid user story\".\n* Document each test case clearly, following the same formatting as the provided test cases.\n* Ensure that the test case numbers are a complete increment of the last given test case for consistency and easy reference.\n*Consider test cases that are realistic and feasible to test within the given testing environment.",
        f"input: {input_text}",
        "output: ",
        ]

         # Generate content using the model 2 
        response = model.generate_content(prompt_parts)
        # Extract the generated text
        ai_output = response.text
    return ai_output

# Function to compute cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b.T) / (np.linalg.norm(a, axis=1)[:, np.newaxis] * np.linalg.norm(b, axis=1))

# Function that present the AI model Pipeline 
async def generate_test_cases(model,input_text,embedded_data):
    db_manager2 = StorySTPDBManager()   # Initialize the database manager

    # calculate the cosine similarity and find the most relevent part from the embedded_data.npy file)
    embedded_input = model.encode(input_text)  # Encode the input text
    embedded_input = embedded_input.reshape(1, -1)  # Reshape the encoded input

    similarities = cosine_similarity(embedded_input, embedded_data)  # Compute cosine similarities
    top_index = np.argmax(similarities)  # Find the index of the most similar entry
    top_cosine_similarity=round(similarities[0][top_index],2) # Round the top cosine similarity

    # Retrieve the STP from the database
    stp = await db_manager2.get_stp_by_index(top_index)

    if top_cosine_similarity >= 0.9:
        output= format_output(stp)

    elif 0.5 <= top_cosine_similarity < 0.9:
        # Augment the input text with a reference
        aug_input_text = f"{input_text}\n(Reference)\n{stp}"
        # Trim the text if it exceeds 30000 words
        if len(aug_input_text.split()) > 30000:  
            aug_input_text = " ".join(aug_input_text.split()[:30000])

        # Generate output1 using model1 (FIRST Call to Gemini API )
        initial_output = model1(aug_input_text)
        
        if "Please enter a valid user story" not in initial_output:
            second_input=f"(User Story:)\n{input_text}\n(Test Cases:)\n{initial_output}"
            # Trim the text if it exceeds 30000 words
            if len(second_input.split()) > 30000:
                second_input = " ".join(second_input.split()[:30000])

            # Generate the second output using model2 to develop more test cases (Second Call to Gemini API )
            second_output = model2(second_input)
            
            # Combine the outputs
            final_output=f"{initial_output}\n{second_output}"
            output=final_output

        else:
            # Set the output if the user story is invalid
            output="Please enter a valid user story."
    else:    
        # Generate initial output using model1
        initial_output = model1(input_text)
        if "Please enter a valid user story" not in initial_output:
            
            # Generate additional output using model2
            second_output = model2(initial_output)

            # Combine the outputs
            final_output=f"{initial_output}\n{second_output}"
            output=final_output

        else:
            # Set the output if the user story is invalid
            output="Please enter a valid user story."

    st.session_state.generated_output = output   # Store the output in the session state
    
# Funtion to Save the new user story and its corresponding test cases to the database
async def save_new_data(model,user_story, stp, embedded_data):
    # Append a new row to the SQLite database with the generated output
    db_manager2 = StorySTPDBManager()
    # Append a new row to the SQLite database with the generated output
    await db_manager2.insert_stp(user_story, stp)
    # embed the new user_story and save it to the embedded data
    new_data = model.encode(user_story)
    # Concatenate the existing and new data
    embedded_data = np.append(embedded_data, [new_data], axis=0)
    # Save the updated data to the file
    np.save("data/embedded_userstories.npy", embedded_data)
