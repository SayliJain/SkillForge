import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Welcome to SkillForge India",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="auto",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .section {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #ddd;
    }
    .emoji {
        font-size: 50px;
        margin-bottom: 10px;
    }
    .title {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        display: block;
        margin-bottom: 5px;
    }
    .description {
        font-size: 18px;
        color: #555;
        margin-bottom: 10px;
    }
    .arrow {
        font-size: 30px;
        color: #007bff;
        text-decoration: none;
    }
    .arrow:hover {
        text-decoration: underline;
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        font-size: 14px;
        color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header section
st.title("🎓 Welcome to SkillForge India")
st.subheader("Empower your career with the right skills!")
st.markdown("Explore our interactive tools and resources below to enhance your skills and prepare for the future!")

# Feature sections with descriptions and links
st.markdown("## 🔍 Features")

sections = [
    ("📈", "Progress Tracker and Personalized Learning Portal", "Track your learning progress and get personalized recommendations for skill development.", "https://progresstrackingskillforge.streamlit.app/"),
    ("📊", "Personalized Job Demand Analyser", "Analyze job trends and receive insights into high-demand skills and career paths.", "https://jobmarketanalyser.streamlit.app/"),
    ("💼", "Interview Companion", "Prepare for your interviews with tailored questions and feedback on your answers.", "https://example.com/virtual-interview-bot"),
    ("🤝", "Mentorship Assistance", "Find the perfect mentor or mentee to guide your career journey.", "https://mentorshipassistance.streamlit.app/"),
    ("👨‍🏫", "Career Assistance Bot", "Get career advice and insights on job roles and industry trends.", "https://careerassist.streamlit.app/"),
    ("📝", "CV Optimizer", "Optimize your resume with actionable suggestions and download the improved version.", "https://cvoptimiser.streamlit.app/"),
    ("📚", "Assessment Helper", "Evaluate your skills with personalized questions and receive a proficiency report.", "https://example.com/student-assessment-bot"),
    ("📖", "Glossary Generator", "Upload a PDF and generate a glossary with key terms and their definitions.", "https://glossary.streamlit.app/"),
    ("🤖", "StudyBuddy", "Get help with your studies, find resources, and stay organized with our StudyBuddy tool.", "https://ourstudybuddy.streamlit.app/"),
    ("🎥", "YouTube Video Summarizer & Notes Creator", "Summarize YouTube videos and extract key notes for efficient learning.", "https://notesgenerator.streamlit.app/")
]

for emoji, title, description, link in sections:
    st.markdown(f"""
    <div class="section">
        <div class="emoji">{emoji}</div>
        <div class="title">{title}</div>
        <div class="description">{description}</div>
        <a href="{link}" target="_blank" class="arrow">➡️</a>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    Team: Init_to_Winit<br>
    Team Members: Sayli, Ratan, Bharath
</div>
""", unsafe_allow_html=True)
