import asyncio
import aiohttp
import streamlit as st
import pandas as pd
import openai
from PyPDF2 import PdfReader
from docx import Document
import ssl
import certifi
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Set your OpenAI API key
openai.api_key = ''

# SSL context setup for secure connections
ssl_context = ssl.create_default_context(cafile=certifi.where())

async def generate_response(prompt):
    async with aiohttp.ClientSession() as session:
        retries = 5
        for attempt in range(retries):
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openai.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are an AI assistant providing detailed and accurate analysis. Your role is to offer insights and recommendations."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1500,
                        "temperature": 0.7
                    },
                    ssl=ssl_context
                ) as response:
                    if response.status == 429:
                        error_message = await response.json()
                        wait_time = int(error_message['error']['message'].split("in ")[1].split("s")[0])
                        st.warning(f"Rate limit reached. Retrying in {wait_time} seconds.")
                        time.sleep(wait_time)
                        continue
                    elif response.status != 200:
                        error_message = f"Error {response.status}: {await response.text()}"
                        st.error(error_message)
                        return f"API request failed: {error_message}"

                    result = await response.json()

                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        st.error("Unexpected API response structure")
                        return "An unexpected error occurred. Please try again later."
            except Exception as e:
                st.error(f"Exception occurred: {str(e)}")
                return f"An exception occurred: {str(e)}"
            break
        else:
            st.error("Exceeded maximum retry attempts.")
            return "Exceeded maximum retry attempts."

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def plot_progress_chart(test_scores):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Date', y='Score', hue='Subject', data=test_scores, marker='o')
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('Progress Over Time by Subject')
    plt.legend(title='Subject')
    st.pyplot(plt)

# Streamlit setup
st.sidebar.header("Navigation")
tabs = [
    "Main Page",
    "Resume Comparison",
    "Test Score Analysis",
    "User Profile",
    "Learning Pathway",
    "Progress Reports"
]
selected_tab = st.sidebar.radio("Select a tab:", tabs)

# Ensure session state for data storage
if 'old_resume_text' not in st.session_state:
    st.session_state.old_resume_text = ""
if 'new_resume_text' not in st.session_state:
    st.session_state.new_resume_text = ""
if 'comparison_report' not in st.session_state:
    st.session_state.comparison_report = ""
if 'test_scores' not in st.session_state:
    st.session_state.test_scores = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = ""
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = ""
if 'learning_goals' not in st.session_state:
    st.session_state.learning_goals = []

# Main Page Content
if selected_tab == "Main Page":
    st.title("📊 Skilling Progress Tracker")
    st.write("Welcome to the Skilling Progress Tracker! Use this tool to track and improve your skills over time.")

    st.markdown("""
    - **Resume Comparison**: Compare your old and new resumes to see your progress.
    - **Test Score Analysis**: Analyze your test scores to identify strengths and weaknesses.
    - **User Profile**: Create a comprehensive user profile based on your progress.
    - **Learning Pathway**: Create a personalized learning pathway based on your profile and goals.
    - **Progress Reports**: Download detailed reports of your progress and achievements.
    """)

# Resume Comparison
if selected_tab == "Resume Comparison":
    st.title("📄 Resume Comparison")
    
    st.header("Upload Old Resume")
    old_resume = st.file_uploader("Choose the old resume file", type=["pdf", "docx"])
    
    st.header("Upload New Resume")
    new_resume = st.file_uploader("Choose the new resume file", type=["pdf", "docx"])
    
    if old_resume and new_resume:
        with st.spinner('Extracting text from resumes...'):
            old_resume_text = extract_text_from_pdf(old_resume) if old_resume.type == "application/pdf" else extract_text_from_docx(old_resume)
            new_resume_text = extract_text_from_pdf(new_resume) if new_resume.type == "application/pdf" else extract_text_from_docx(new_resume)
        
        st.session_state.old_resume_text = old_resume_text
        st.session_state.new_resume_text = new_resume_text
        
        prompt = f"""
        Compare the following resumes, highlight the new things and provide a detailed analysis:
        
        1. **User Information**:
            - Extract the user's name, age, current working or education status.
        
        2. **Education and Certifications**:
            - Highlight progress in education, new degrees, diplomas, certifications, and courses completed.
        
        3. **Project Progress**:
            - Detail progress in projects, including new projects, roles, and responsibilities. Extract the new learnings in projects
        
        4. **Skills Comparison**:
            - Mention old and new skills, highlighting improvements or new skills acquired.
        
        5. **Recommendations**:
            - Provide actionable recommendations for further improvement in education, skills, and career development.
        Mention everything in a structured format, don't use the words in the new or old resume, but rather use words to showcase progress in general
        
        Old Resume:
        {old_resume_text}
        
        New Resume:
        {new_resume_text}
        """
        comparison_report = asyncio.run(generate_response(prompt))
        st.session_state.comparison_report = comparison_report
        
        st.subheader("Resume Comparison Report")
        st.write(comparison_report)

# Test Score Analysis
if selected_tab == "Test Score Analysis":
    st.title("📊 Test Score Analysis")
    
    uploaded_csv_file = st.file_uploader("Upload your test scores CSV file", type="csv")
    
    if uploaded_csv_file is not None:
        test_scores = pd.read_csv(uploaded_csv_file)
        st.session_state.test_scores = test_scores
    
        st.write("Uploaded Test Scores Data")
        st.write(test_scores)
        
        test_data_sample = test_scores.head(5).to_string()
        prompt = f"""
        Analyze the following test scores:
        1. Identify the areas of improvement in each subject and suggest possible methods for improvement.
        2. Compare the performance between different subjects and over time.
        3. Include section-wise and question-wise analysis to identify specific strengths and weaknesses.
        4. Highlight trends and provide recommendations for consistent performance improvement.
        
        Test Data:
        {test_data_sample}
        """
        analysis_report = asyncio.run(generate_response(prompt))
        st.session_state.analysis_report = analysis_report
        
        st.subheader("Strengths and Weaknesses Report")
        st.write(analysis_report)

        # Visualize test scores
        st.subheader("Visualize Your Test Scores")
        fig, ax = plt.subplots()
        sns.barplot(x='Date', y='Score', hue='Subject', data=test_scores, ax=ax)
        plt.title('Test Scores by Date and Subject')
        st.pyplot(fig)

        # Plot progress chart
        plot_progress_chart(test_scores)
    else:
        st.warning("Please upload a CSV file to proceed with the analysis.")

# User Profile
if selected_tab == "User Profile":
    st.title("🔍 User Profile")
    
    if 'comparison_report' in st.session_state and 'analysis_report' in st.session_state:
        comparison_report = st.session_state.comparison_report
        analysis_report = st.session_state.analysis_report
        
        profile_prompt = f"""
        Based on the resume comparison and test score analysis, create a comprehensive user profile that includes the following sections:
        
        1. **Basic Information**:
           - Name, age, and current working or educational status.
        
        2. **Educational Background and Certifications**:
           - Detailed overview of the user's educational history, including institutions attended, degrees earned, and certifications obtained. Highlight any new qualifications or courses completed recently.
        
        3. **Professional Experience and Projects**:
           - A summary of the user's professional experience, focusing on significant roles, responsibilities, and achievements. Include details about projects worked on, with an emphasis on new projects, roles undertaken, and skills learned.
        
        4. **Skills Profile**:
           - A comprehensive list of the user's skills, distinguishing between existing skills and newly acquired skills. Highlight areas of significant improvement and emerging skills relevant to the user's career goals.
        
        5. **Strengths and Areas for Improvement**:
           - An analysis of the user's strengths, with specific examples drawn from their educational and professional background. Identify areas for improvement, providing actionable suggestions for skill enhancement and career development.
        
        6. **Career and Learning Goals**:
           - Outline the user's short-term and long-term career goals, based on the analysis of their profile. Suggest potential learning pathways and skill development opportunities to help achieve these goals.
        
        7. **Recommendations**:
           - Personalized recommendations for further education, skill acquisition, and career advancement. Include suggestions for resources, courses, or experiences that would be beneficial based on the user's current profile.
        
        Ensure that the user profile is structured, detailed, and provides a clear overview of the user's progress, achievements, and future potential.
        
        Resume Comparison:
        {comparison_report}
        
        Test Score Analysis:
        {analysis_report}
        """
        user_profile = asyncio.run(generate_response(profile_prompt))
        st.session_state.user_profile = user_profile
        
        st.subheader("User Profile")
        st.write(user_profile)
    else:
        st.warning("Please complete the resume comparison and test score analysis first.")

# Learning Pathway
if selected_tab == "Learning Pathway":
    st.title("📚 Learning Pathway")
    
    st.header("Set Learning Goals")
    goal = st.text_input("Enter a learning goal:")
    if st.button("Add Goal"):
        st.session_state.learning_goals.append(goal)
        st.success("Goal added!")

    if st.session_state.learning_goals:
        st.write("### Your Learning Goals:")
        for idx, goal in enumerate(st.session_state.learning_goals, 1):
            st.write(f"{idx}. {goal}")

    st.header("Personalized Learning Pathway")
    subject = st.text_input("Enter the subject you want to learn:")
    time_per_day = st.number_input("Enter the number of hours you can dedicate per day:", min_value=0, max_value=24, step=1)
    
    if st.button("Generate Learning Pathway"):
        if 'user_profile' in st.session_state:
            user_profile = st.session_state.user_profile
            pathway_prompt = f"Based on the user profile:\n{user_profile}\n\nCreate a personalized learning pathway for learning {subject} with {time_per_day} hours per day."
            learning_pathway = asyncio.run(generate_response(pathway_prompt))
            
            st.subheader("Personalized Learning Pathway")
            st.write(learning_pathway)
        else:
            st.warning("Please create a user profile first.")

# Progress Reports
if selected_tab == "Progress Reports":
    st.title("📄 Download Progress Report")
    
    if st.button("Generate and Download Report"):
        st.warning("PDF downloading functionality has been removed.")
