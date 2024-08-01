import os
import requests
from bs4 import BeautifulSoup
import openai
import pdfplumber
import streamlit as st

# Function to scrape job titles
def scrape_job_titles(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        job_titles = soup.select("#main-content section:nth-of-type(2) ul li div a span")
        job_title_texts = [job_title.get_text(strip=True) for job_title in job_titles]
        return job_title_texts
    except Exception as e:
        st.error(f"Error occurred during the request: {e}")
        return []

# Function to analyze job titles using OpenAI GPT-4
def analyze_job_titles(job_titles):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        "Here are the job titles scraped from LinkedIn:\n"
        + "\n".join(job_titles) + "\n\n"
        "Analyze these job titles and provide a summary of the 3 most trending domains and job titles, also give a one line description as to why it is in demand. Don't include an introductory sentence. "
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

# Function to provide personalized insights using OpenAI GPT-4
def provide_personalized_insights(user_profile_text, job_titles_analysis):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        f"User profile information:\n{user_profile_text}\n\n"
        f"Job titles analysis:\n{job_titles_analysis}\n\n"
        "Based on the user's profile, provide personalized insights and advice for these job trends."
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful career advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

# Main Streamlit application
def main():
    st.title("Personalized Job Demand Analysis")

    position = st.text_input("Enter location:")
    pdf_file = st.file_uploader("Upload your profile PDF", type=["pdf"])

    if st.button("Analyze Job Trends and Get Insights"):
        if position:
            url = f"https://in.linkedin.com/jobs/trends-in-jobs-{position}"
            job_titles = scrape_job_titles(url)

            if job_titles:
                st.write("\nAnalyzing job titles...\n")
                analysis = analyze_job_titles(job_titles)
                st.subheader("Analysis")
                st.write(analysis)

                if pdf_file:
                    user_profile_text = extract_text_from_pdf(pdf_file)

                    st.write("\nProviding personalized insights...\n")
                    personalized_insights = provide_personalized_insights(user_profile_text, analysis)
                    st.subheader("Personalized Insights")
                    st.write(personalized_insights)
                else:
                    st.error("Please upload a profile PDF file.")
            else:
                st.error("No job titles found.")
        else:
            st.error("Please enter a location.")

if __name__ == "__main__":
    main()
