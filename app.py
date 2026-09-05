import streamlit as st
import pypdf
from google import genai
from google.genai import types

# Global model definition
MODEL_NAME = 'gemini-3.6-flash'

# Page Configuration
st.set_page_config(page_title="Academic AI Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic AI Assistant")
st.write("Upload study materials, ask questions, or generate study plans and quizzes!")

# Sidebar - API Key Input
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.info("Obtain a free key from [Google AI Studio](https://aistudio.google.com/).")

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# Main App Logic
if api_key:
    client = genai.Client(api_key=api_key)
    
    # Feature Selection Tabs
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
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=prompt,
                        )
                        st.markdown("### Answer:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")

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
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=prompt,
                        )
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")
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
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=prompt,
                        )
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")
            else:
                st.warning("Please specify a topic.")
else:
    st.warning("Please enter your Gemini API key in the sidebar to activate the bot.")
