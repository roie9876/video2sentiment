import streamlit as st
st.set_page_config(layout="wide")  
import SessionState

# Import your scripts
import video2sentiment_upload
import video2semtiment_ui
import video2semtiment_openai

# Create a function for each page
def page_video2sentiment_upload():
    video2sentiment_upload.main()  # Assuming main() is the entry point of your script

def page_video2semtiment_openai():
    video2semtiment_openai.main()  # Assuming main() is the entry point of your script    

def page_video2semtiment_ui():
    video2semtiment_ui.main()  # Assuming main() is the entry point of your script

def page_video2sentiment_delete():
    video2sentiment_delete.main()  # Assuming main() is the entry point of your script

# Create a dictionary of pages and their corresponding functions
pages = {
    "Upload Video": page_video2sentiment_upload,
    "Run AI on Speech": page_video2semtiment_openai,
    "Speech Investigation": page_video2semtiment_ui,
    "Speech Delete": page_video2sentiment_delete
}

# Create a SessionState object
state = SessionState.get()

# Create a sidebar for navigation
page = st.sidebar.selectbox("Select a page", options=list(pages.keys()), index=state.page_index)

# Call the corresponding function
pages[page]()

# Update the index of the selected page
state.page_index = list(pages.keys()).index(page)