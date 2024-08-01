import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
# Load synthetic mentor data
mentors_df = pd.read_csv('synthetic_mentors.csv')

# Database setup
conn = sqlite3.connect('mentorship.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT,
              user_type TEXT,
              domain TEXT,
              answers TEXT,
              timestamp DATETIME)''')
conn.commit()

def populate_database_with_mentors():
    for _, mentor in mentors_df.iterrows():
        c.execute("INSERT OR IGNORE INTO users (username, user_type, domain, answers, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (mentor['username'], 'mentor', mentor['domain'], mentor['bio'], mentor['joined_date']))
    conn.commit()

# Populate the database with synthetic data
populate_database_with_mentors()


import streamlit as st
import sqlite3
import openai
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
# Set up OpenAI API key
# openai.api_key = st.secrets["openai_api_key"]
client = openai.OpenAI(api_key='openai.api_key')
# Database setup
conn = sqlite3.connect('mentorship.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT,
              user_type TEXT,
              domain TEXT,
              answers TEXT,
              timestamp DATETIME)''')
conn.commit()

def generate_questions(user_type, domain):
    prompt = f"Generate 5 questions for a {user_type} in the {domain} domain for a mentorship program."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    questions = response.choices[0].message.content.strip().split('\n')
    return questions

def save_user(username, user_type, domain, answers):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO users (username, user_type, domain, answers, timestamp) VALUES (?, ?, ?, ?, ?)",
              (username, user_type, domain, answers, timestamp))
    conn.commit()

def get_mentors(domain):
    c.execute("SELECT username, answers FROM users WHERE user_type='mentor' AND domain=?", (domain,))
    return c.fetchall()

def match_algorithm(mentee_answers, mentors):
    prompt = f"Given the mentee's answers: {mentee_answers}, and the following mentor profiles: {mentors}, rank the top 3 most suitable mentors based on their compatibility. Return only the usernames of the top 3 mentors in order of best match."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    matched_mentors = response.choices[0].message.content.strip().split('\n')
    return matched_mentors[:3]

def main():
    st.title("Mentorship Program")

    # Query and display mentors
    c.execute("SELECT * FROM users WHERE user_type='mentor'")
    mentors = c.fetchall()
    # st.write("Mentors:")
    # st.dataframe(mentors)
    user_type = st.radio("Choose your role:", ("Mentor", "Mentee"))

    if user_type:
        st.write(f"You've selected: {user_type}")
        username = st.text_input("Enter your username:")
        domain = st.text_input("Enter your domain of expertise:")

        if st.button("Continue"):
            questions = generate_questions(user_type.lower(), domain)
            st.session_state.user_info = {
                'username': username,
                'user_type': user_type.lower(),
                'domain': domain,
                'questions': questions
            }
            st.rerun()

    if 'user_info' in st.session_state:
        st.write("Please answer the following questions:")
        answers = []
        for q in st.session_state.user_info['questions']:
            answer = st.text_input(q)
            answers.append(answer)

        if st.button("Submit"):
            answers_str = ','.join(answers)
            save_user(st.session_state.user_info['username'],
                      st.session_state.user_info['user_type'],
                      st.session_state.user_info['domain'],
                      answers_str)
            
            if st.session_state.user_info['user_type'] == 'mentee':
                mentors = get_mentors(st.session_state.user_info['domain'])
                matched_mentors = match_algorithm(answers_str, mentors)
                st.write("Matched Mentors:")
                for mentor in matched_mentors:
                    st.write(f"- {mentor}")
            else:
                st.write("Thank you for registering as a mentor!")

            del st.session_state.user_info

if __name__ == "__main__":
    main()