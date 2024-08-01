import streamlit as st
import openai
import docx2txt
import PyPDF2
import io
from docx import Document
from io import BytesIO
import warnings

# Set up OpenAI API key
client = openai.OpenAI(api_key='')

def extract_text_from_doc(file):
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    else:
        text = docx2txt.process(file)
    return text

# def optimize_resume(resume_text, job_description):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a professional resume optimizer. Analyze the given resume and job description, then provide suggestions for improvement and optimization."},
#             {"role": "user", "content": f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}\n\nPlease optimize the resume for this job description. Provide suggestions for improvements, skills to highlight, and certifications that could be beneficial."}
#         ]
#     )
#     return response.choices[0].message.content.strip()

def optimize_resume(resume_text, job_description):
    system_message = """You are an expert resume optimizer and career coach. Your task is to analyze the provided resume and job description, then provide detailed, specific suggestions to optimize the resume for the given job."""

    user_message = f"""Please analyze the following resume and job description, then provide detailed optimization suggestions following these guidelines:

1. Highlight key skills and experiences from the resume that directly match the job requirements.
2. Suggest 3-5 specific achievements or projects from the resume that should be emphasized, including metrics where possible.
3. Identify any gaps between the resume and job requirements, and recommend ways to address them.
4. Propose 2-3 relevant certifications or training programs that could enhance the candidate's qualifications for this role.
5. Suggest 5-7 industry-specific keywords from the job description that should be incorporated into the resume.
6. Recommend improvements to the resume structure, formatting, or sections to better align with industry standards for this type of role.
7. Provide a brief (2-3 sentence) tailored professional summary that encapsulates the candidate's most relevant qualifications for this specific job.
8. Suggest any soft skills or personal attributes mentioned in the job description that the candidate should highlight.
9. If applicable, recommend ways to explain any career gaps or transitions in a positive light.
10. Provide 2-3 specific suggestions for tailoring the resume's language and tone to match the company culture, based on the job description and any available information about the company.

Please provide your recommendations in a clear, bullet-point format under relevant headings. Be as specific and actionable as possible in your suggestions.

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip()


def create_download_document(optimized_text):
    doc = Document()
    doc.add_paragraph(optimized_text)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

st.title("Resume Optimizer")

uploaded_file = st.file_uploader("Upload your resume (DOC, DOCX, or PDF)", type=["doc", "docx", "pdf"])
job_description = st.text_area("Enter the job description")

if uploaded_file and job_description:
    resume_text = extract_text_from_doc(uploaded_file)
    
    if st.button("Optimize Resume"):
        with st.spinner("Optimizing your resume..."):
            optimized_resume = optimize_resume(resume_text, job_description)
        
        st.subheader("Optimized Resume and Suggestions")
        st.write(optimized_resume)
        
        doc_download = create_download_document(optimized_resume)
        st.download_button(
            label="Download Optimized Resume",
            data=doc_download,
            file_name="optimized_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.sidebar.title("About")
st.sidebar.info("This app uses OpenAI's GPT-3.5-turbo model to optimize your resume based on a job description. Upload your resume and enter the job description to get personalized suggestions and improvements.")
