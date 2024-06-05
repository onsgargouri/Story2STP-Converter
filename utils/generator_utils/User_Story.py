import re
import string

# Function to remove punctuation characters 
def remove_punctuation(text):    
    # Remove all punctuation characters from the text
    user_story = ''.join(char for char in text if char not in string.punctuation )
    return user_story

# Function to convert a Jira formatted table to Markdown format
def markdown_table(user_story):
    # Strip leading and trailing whitespaces and split the text into lines
    lines = user_story.strip().split('\n')
    markdown_content = ""
    header_processed = False
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            # Process the table header and add Markdown table header separator
            if not header_processed:
                markdown_content += line + '\n'
                markdown_content += "| " + " | ".join(["---"] * (line.count('|') - 1)) + " |\n"
                header_processed = True
            else:
                # Process table rows
                markdown_content += line + '\n'
        else:
            # Add non-table lines with extra newlines for spacing
            markdown_content += line + '\n\n'
    return markdown_content.strip()

#Function to remove Jira formatting elements and format the user-story 
def remove_formatting(user_story):
    # Define regex patterns for different Jira formatting elements
    formatting_patterns = {
        "headings": r'(?i)h\d\.', # Matches headings like h1., h2., etc.
        "block_quotaion": r'bq\.', # Matches block quotations
        "color": r'\{color[^}]*\}.*?\{color\}', # Matches color formatting
        "images": r'!image.*?!', # Matches image tags
        "attachments": r'!media.*?!', # Matches attachment tags
        "panels": r'\{panel[^}]*\}', # Matches panel formatting
        "code": r'\{code[^}]*\}' # Matches code formatting
    }

    # Remove each formatting pattern from the user story
    for key, value in formatting_patterns.items():
        user_story = re.sub(value, '', user_story)

    # Convert Jira  tables (if exist) to Markdown table format
    user_story=markdown_table(user_story)
    
    # Remove punctuation from the user story
    remove_punctuation(user_story)
    user_story = user_story.replace('*', '**') # Preserve bold text by converting Jira bold formatting to Markdown bold 
    user_story = user_story.replace('+', '  ------  ') # Replace '+' with a custom separator for clarity in Markdown
    
    # Replace multiple consecutive whitespaces with newlines for better readability
    user_story = re.sub(r'\s{5,}', '\n\n', user_story)
    
    return user_story

#Function to remove Hyperlinks from user-story
def remove_hyperlinks(user_story):
    # Remove hyperlinks in the format [text|url]
    user_story = re.sub(r'\[([^\]]*?)\|https?://.*?\]', r'\1', user_story) 
    
    # Remove hyperlinks in the format |url|
    user_story=re.sub(r'https?://.*?\|', '', user_story) 
    return user_story




