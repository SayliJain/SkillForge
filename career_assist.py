import streamlit as st
import openai
from datetime import datetime
import os
import pandas as pd        
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set up OpenAI API key
client = openai.OpenAI(api_key='openai.api_key')

def get_bot_response(prompt, conversation_history):
    messages = [
        {"role": "system", "content": "You are a knowledgeable career advisor specializing in various professional domains. Your goal is to provide accurate and helpful information about careers, job roles, and industry trends."},
    ] + conversation_history + [
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

st.title("Career Advisor Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me about careers, job roles, or industry trends"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = get_bot_response(prompt, st.session_state.messages)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.title("About")
st.sidebar.info("This chatbot uses OpenAI's GPT-3.5-turbo model to provide information and advice on careers, job roles, and industry trends. Feel free to ask any career-related questions!")
