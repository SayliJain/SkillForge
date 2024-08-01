import os
import numpy as np
from numpy.linalg import norm
import pdfplumber
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import openai
import json
import random

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
# Initialize the OpenAI client
client = OpenAI()

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

# Function to generate questions using OpenAI's GPT-3.5 Turbo
def generate_questions(text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Without any explanatory text, given the following text, generate a list of relevant questions:\n\n{text}. Make sure to not include any preceding explanatory text whatsoever, and just start off with the questions."}
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        generated_text = response.choices[0].message.content.strip()
        questions = generated_text.split('\n')
        return questions
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Function to determine the topic of each question
def determine_topic(question, text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Based on the following text, determine the topic of the given question and be pretty specific about the topics:\n\nText: {text}\n\nQuestion: {question}\n\nProvide only the topic."}
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=50
        )
        topic = response.choices[0].message.content.strip()
        return topic
    except Exception as e:
        print(f"An error occurred while determining the topic for question '{question}': {e}")
        return "Unknown"

# Function to generate answers for each question using the LLM
def generate_answers(text, questions_with_topics):
    answers = []
    for question, topic in questions_with_topics:
        try:
            prompt = f"Answer the following question based on the text provided:\n\nQuestion: {question}\n\nText: {text} Structre your output properly with bullet points or numbers or whatever is easily readable and user friendly."
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=150
            )
            answer = response.choices[0].text.strip()
            answers.append((question, topic, answer))
        except Exception as e:
            print(f"An error occurred while generating answer for question '{question}': {e}")
            answers.append((question, topic, "No answer generated."))
    return answers

# Function to get embeddings with retry logic
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model="text-embedding-3-small") -> list:
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# Function to evaluate answers and provide feedback
def evaluate_student_answer_advanced(system_answer, user_answer):
    try:
        system_embedding = get_embedding(system_answer)
        user_embedding = get_embedding(user_answer)
        cosine_sim = np.dot(system_embedding, user_embedding) / (norm(system_embedding) * norm(user_embedding))
        similarity_percentage = (cosine_sim + 1) / 2 * 100
        if similarity_percentage < 75:  # Assuming a threshold for correctness
            print("Your answer is incorrect.")
            print(f"Correct answer: {system_answer}")
        else:
            print("Your answer is correct.")
        return similarity_percentage
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

def summarize_text(text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ]        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300  # Adjust based on how concise the summary needs to be
        )
        summary =  response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"An error occurred during text summarization: {e}")
        return text 

# Function to generate proficiency report
def generate_proficiency_report(questions_with_topics, answers, user_answers):
    report = {}
    for (question, topic, system_answer), user_answer in zip(answers, user_answers):
        similarity_percentage = evaluate_student_answer_advanced(system_answer, user_answer)
        if topic not in report:
            report[topic] = {"correct": 0, "total": 0}
        if similarity_percentage >= 75:
            report[topic]["correct"] += 1
        report[topic]["total"] += 1
    return report

# Function to save proficiency report
def save_proficiency_report(report, file_path):
    with open(file_path, 'w') as file:
        json.dump(report, file, indent=4)

# Function to check for preexisting report and determine progress
def check_progress(new_report, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            old_report = json.load(file)
        progress_report = {}
        for topic in new_report:
            old_correct = old_report.get(topic, {}).get("correct", 0)
            old_total = old_report.get(topic, {}).get("total", 0)
            new_correct = new_report[topic]["correct"]
            new_total = new_report[topic]["total"]
            old_percentage = (old_correct / old_total) * 100 if old_total > 0 else 0
            new_percentage = (new_correct / new_total) * 100 if new_total > 0 else 0
            progress = new_percentage - old_percentage
            progress_report[topic] = progress
        return progress_report
    return None

# Main interaction loop
def main():
    pdf_path = r"C:\Users\Ratan\Desktop\notes1.pdf"
    report_file_path = "proficiency_report.json"
    pdf_text = extract_text_from_pdf(pdf_path)
    summarized_text = summarize_text(pdf_text)  # Summarize the text to reduce token count
    questions = generate_questions(summarized_text)
    questions_with_topics = [(question, determine_topic(question, summarized_text)) for question in questions]
    answers = generate_answers(summarized_text, questions_with_topics)
    user_answers = []
    for question, topic, system_answer in answers:
        print("Question:", question)
        user_answer = input("Your answer: ")
        user_answers.append(user_answer)
    new_report = generate_proficiency_report(questions_with_topics, answers, user_answers)
    save_proficiency_report(new_report, report_file_path)
    progress_report = check_progress(new_report, report_file_path)
    if progress_report:
        print("Progress Report:")
        for topic, progress in progress_report.items():
            print(f"Topic: {topic}, Progress: {progress:.2f}%")

if __name__ == "__main__":
    main()
