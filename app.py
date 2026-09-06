import streamlit as st
import pypdf
import time
from google import genai
from google.genai import types

# Priority sequence of Gemini models with separate capacity pools
FALLBACK_MODELS = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash']

# Page Configuration
st.set_page_config(page_title="Academic AI Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic AI Assistant")
st.write("Upload study materials, ask questions, or generate study plans and quizzes!")

# Sidebar - API Key Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.info("Obtain a free key from [Google AI Studio](https://aistudio.google.com/).")

# Helper function to extract text from an uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# Robust helper function to handle 503 capacity limits across multiple model pools
def generate_content_with_retry(client, prompt, max_retries=2):
    """
    Cycles through available model pools and performs retries with backoff delays 
    if capacity limits (503/UNAVAILABLE) occur.
    """
    last_exception = None
    for model_id in FALLBACK_MODELS:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_exception = e
                # Wait 2 seconds before retrying or switching endpoints
                time.sleep(2)
                continue
                
    # Raise the final exception if all models fail
    raise last_exception

# Main App Execution
if api_key:
    client = genai.Client(api_key=api_key)
    
    # Feature Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Document Q&A", "📅 Study Planner", "📝 Quiz Generator"])
    
    # TAB 1: Document Q&A
    with tab1:
        st.subheader("Upload Notes / Syllabus / PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if uploaded_file:
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.success(f"Successfully loaded '{uploaded_file.name}'!")
            
            user_question = st.text_input("Ask a question about this document:")
            if user_question:
                prompt = f"""
                You are an expert academic tutor. Answer the student's question accurately using ONLY the context provided below.
                If the answer cannot be found in the text, inform the user clearly.
                
                Context:
                {pdf_text[:10000]}
                
                Question: {user_question}
                """
                with st.spinner("Analyzing document..."):
                    try:
                        answer = generate_content_with_retry(client, prompt)
                        st.markdown("### Answer:")
                        st.write(answer)
                    except Exception as e:
                        st.error("The Gemini servers are experiencing heavy global demand. Please wait a few seconds and try clicking submit again.")

    # TAB 2: Study Planner
    with tab2:
        st.subheader("Generate an Automated Study Plan")
        subject = st.text_input("Subject Name (e.g., Data Structures, Organic Chemistry):")
        days = st.number_input("Days available before exam:", min_value=1, max_value=60, value=7)
        hours = st.number_input("Daily study hours:", min_value=1, max_value=12, value=3)
        
        if st.button("Generate Plan"):
            if subject:
                prompt = f"Create a detailed day-by-day study timetable for {subject} spanning {days} days, with {hours} hours of study per day. Format as structured Markdown."
                with st.spinner("Creating schedule..."):
                    try:
                        plan = generate_content_with_retry(client, prompt)
                        st.markdown(plan)
                    except Exception as e:
                        st.error("The Gemini servers are experiencing heavy global demand. Please wait a few seconds and try clicking again.")
            else:
                st.warning("Please specify a subject.")

    # TAB 3: Quiz Generator
    with tab3:
        st.subheader("Generate Practice Quizzes")
        topic = st.text_input("Topic for Quiz:")
        num_questions = st.slider("Number of Questions:", 3, 10, 5)
        
        if st.button("Generate Quiz"):
            if topic:
                prompt = f"Generate a {num_questions}-question multiple-choice quiz on '{topic}'. Include 4 choices per question and provide the correct answer key with short explanations at the end."
                with st.spinner("Generating quiz..."):
                    try:
                        quiz = generate_content_with_retry(client, prompt)
                        st.markdown(quiz)
                    except Exception as e:
                        st.error("The Gemini servers are experiencing heavy global demand. Please wait a few seconds and try clicking again.")
            else:
                st.warning("Please specify a topic.")
else:
    st.warning("Please enter your Gemini API key in the sidebar to activate the bot.")
