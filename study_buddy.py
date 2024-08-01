import streamlit as st
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import openai
from io import BytesIO
import os

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="StudyBuddy")

def process_pdfs(pdf_files):
    raw_text = ''
    for pdf_file in pdf_files:
        pdf_bytes = pdf_file.getvalue()
        pdf_io = BytesIO(pdf_bytes)
        pdfreader = PdfReader(pdf_io)
        for page in pdfreader.pages:
            content = page.extract_text()
            if content:
                raw_text += content
    return raw_text

def create_vectorstore(texts):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(texts)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, embeddings, model

def find_context(query, index, embeddings, model, texts, top_k=5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    relevant_texts = [texts[i] for i in indices[0]]
    return " ".join(relevant_texts)

def chatbot(prompt, chat_history, context):
    messages = [{"role": "system", "content": """You are a study buddy for students. 
Your goal is to help students understand their study material thoroughly, 
whether they are textbooks, lecture notes, or any educational content.
Use the provided context to answer questions accurately and clearly. 
Provide concise answers in a simple, understandable language and in short by default, 
but if the user asks for a detailed explanation, provide a more detailed response.
Ensure your answers are consistent with the provided context and any previous interactions. 
If the user greets you or asks about a general topic, greet them back warmly 
and provide a brief response on the general topic before continuing with their main question.
Your aim is to be helpful, friendly, and thorough, ensuring the student leaves with a clear understanding of the material."""}]
    
    for message in chat_history:
        messages.append({"role": message["role"], "content": message["content"]})
    
    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})
    
    messages.append({"role": "user", "content": prompt})
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content.strip()


def history(role, content, chat_history):
    chat_history.append({"role": role, "content": content})
    return chat_history

def main():
    st.title("StudyBuddy")

    uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])
    if uploaded_files:
        raw_text = process_pdfs(uploaded_files)
        st.write("PDFs processed successfully!")

    if uploaded_files:
        all_texts = [raw_text]
        index, embeddings, model = create_vectorstore(all_texts)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You: ", key="input")
    if user_input:
        context = find_context(user_input, index, embeddings, model, all_texts) if uploaded_files else ""
        st.session_state.chat_history = history("user", user_input, st.session_state.chat_history)
        gpt_response = chatbot(user_input, st.session_state.chat_history, context)
        st.session_state.chat_history = history("assistant", gpt_response, st.session_state.chat_history)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                st.write(message['content'])

if __name__ == "__main__":
    main()
