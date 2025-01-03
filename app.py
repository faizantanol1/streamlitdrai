import streamlit as st
import os
import datetime
import google.generativeai as genai

# Configure Generative AI
try:
    # Replace with your actual API key
    api_key = st.secrets["api"]["API_KEY"]

    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error("API key is not configured in Streamlit secrets.")
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
except Exception as e:
    st.error("Failed to initialize AI model. Please check the API key.")
    model = None

# Directory for uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
document_summary = None

def generate_summary(file_path):
    """
    Generate a summary by uploading the document to Gemini.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return genai.upload_file(file_path, display_name="Gemini 1.5 PDF")
    except Exception as e:
        return str(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# Streamlit App
st.title("Medical Report Analysis Chatbot")

# File Upload Section
st.header("Upload a Biochemistry Report")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    filename, file_extension = os.path.splitext(uploaded_file.name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    doc_id = f"{filename}_{timestamp}"
    file_path = os.path.join(UPLOAD_FOLDER, f"{doc_id}{file_extension}")

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Generate summary
    st.info("Processing the uploaded file...")
    document_summary = generate_summary(file_path)
    if document_summary:
        st.success("Document loaded!")
    else:
        st.error("Failed to generate document summary.")

# Chatbot Section
st.header("Chat with the AI Bot")

if document_summary:
    user_input = st.text_input("Enter your question:")
    if st.button("Send"):
        if user_input:
            try:
                # Define the prompt
                prompt = f"""
                You are an authorized AI assistant working with a doctor to analyze patient medical biochemistry reports. Your role is to interpret the overall results of the reports, guide for patients about their medication according to your knowledge (Dr will review this), and explain the findings in simple words clearly.

                **Patient ID:** N/A

                **Report Summary:** {document_summary}

                User Input: {user_input}
                """

                # Generate content using the model
                response = model.generate_content([document_summary, prompt])
                st.markdown(f"**Bot Response:**\n\n{response.text}")
            except Exception as e:
                st.error(f"Error generating response: {e}")
        else:
            st.warning("Please enter a question.")
else:
    st.warning("Please upload a file to start the analysis.")
