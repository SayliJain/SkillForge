import os
import streamlit as st
import pdfplumber
import openai
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key
client = OpenAI()

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

# Function to summarize text using OpenAI's GPT-3.5 Turbo
def summarize_text(text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500  # Adjust based on how concise the summary needs to be
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        st.error(f"An error occurred during text summarization: {e}")
        return text

# Function to generate glossary terms using OpenAI's GPT-3.5 Turbo
def generate_glossary_terms(text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"You are creating a glossary. Extract key terms from the following text:\n\n{text}"}
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        generated_text = response.choices[0].message.content.strip()
        terms = generated_text.split('\n')
        return terms
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to generate definitions for each term using OpenAI's GPT-3.5 Turbo
def generate_definitions(terms, text):
    definitions = {}
    for term in terms:
        try:
            prompt = f"Define the following term:\n\nTerm: {term} based on the context from this text: \n\n{text}"
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=150
            )
            definition = response.choices[0].text.strip()
            definitions[term] = definition
        except Exception as e:
            st.error(f"An error occurred while generating definition for term '{term}': {e}")
            definitions[term] = "No definition generated."
    return definitions

# Streamlit app
def main():
    st.title("PDF Glossary Creator")
    st.header("Upload a PDF to generate a glossary")

    # Upload PDF file
    pdf_file = st.file_uploader("Upload your PDF", type="pdf")

    if pdf_file is not None:
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_file)
        
        # Summarize the text to reduce token count
        summarized_text = summarize_text(pdf_text)
        
        # Generate glossary terms
        glossary_terms = generate_glossary_terms(summarized_text)
        st.subheader("Glossary Terms")
        st.write(glossary_terms)

        # Generate definitions for glossary terms
        glossary_definitions = generate_definitions(glossary_terms, summarized_text)
        st.subheader("Glossary")
        for term, definition in glossary_definitions.items():
            st.write(f"**{term}**: {definition}")

if __name__ == "__main__":
    main()
