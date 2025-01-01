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

# Path to the static file
# Replace with the actual file path
STATIC_FILE_PATH = "uploads/PDF REPORT_20241219185722.pdf"


def generate_summary(file_path):
    """
    Generate a summary by uploading the document to Gemini.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        summary = genai.upload_file(file_path, display_name="Gemini 1.5 PDF")
        return summary.get("summary", "Summary not returned by Gemini API")
    except Exception as e:
        return str(e)

# Set up the page layout
st.set_page_config(page_title="Chatbot Interface")

    # Add the logo at the top-left corner (replace with your logo's path)
st.image("assets/F3png.png" ,width=200)  # Update with actual logo path


# Add the title of the app
st.title("Ask About Your Medical Lab Reports.")
st.subheader("This is your Doc AI.")

# Load the static file and generate a summary
if os.path.exists(STATIC_FILE_PATH):
    document_summary = generate_summary(STATIC_FILE_PATH)
    if document_summary:
        st.success("Report Summary Loaded")
    else:
        st.error("Failed to generate a summary. Please check the file.")
else:
    st.error("Static file not found. Please check the file path.")

# Chatbot Interface
if "document_summary" in locals():
    st.write("Ask your questions about the report below:")
    user_input = st.text_input("Your question:")
    if st.button("Send"):
        if user_input:
            try:
                prompt = f"""
                        You are an authorized AI assistant working with a doctor to analyze patient medical biochemistry reports. Your role is to interpret the overall results of the reports, guide for patients about their medication according to your knowldge (Dr will review this), and explain the findings in sinple way clearly.

                        **Patient ID:** patient_id or 'N/A'

                        **Report Summary:**  
                        <Summary of the biochemistry report findings>
                        example : XYZ property range (High , Low ) grade: severe , mild etc

                        <AI Dr precription>

                            Elevated ALT and ALP (Liver Enzymes)
                            Silymarin (Milk Thistle) - 140 mg, twice daily after meals

                            Ursodeoxycholic Acid (UDCA) - 300 mg, twice daily

                            Vitamin E - 400 IU, once daily with food

                            N-Acetylcysteine (NAC) - 600 mg, twice daily

                            Proteinuria (Slightly Elevated Urine Protein Levels)
                            Lisinopril - 5 mg, once daily

                            Alternatively: Losartan - 50 mg, once daily

                            Omega-3 Fatty Acids - 1,000 mg, once daily

                            Follow-up and Monitoring:
                            Repeat urine protein test in 2-4 weeks.

                            Monitor blood pressure if ACE inhibitors or ARBs are prescribed.
                        **Medication Guidance:**  
                        - <Medication 1 and its usage instructions>  
                        - <Medication 2 and its usage instructions>  

                        **Recommendations:**  
                        - <Helpful simple words Recommendation 1>  
                        - <Helpful simple words Recommendation 2>  

                        Must Ensure the output is clear, short, simple for normal persons and well-organized in this Markdown format.
                        User Input: {user_input}
                        """
                response = model.generate_content([prompt])
                st.write(f"**AI Response:** {response.text}")
            except Exception as e:
                st.error(f"Error generating response: {e}")
        else:
            st.warning("Please enter a question.")
else:
    st.warning("No summary available. Ensure the report is accessible.")
