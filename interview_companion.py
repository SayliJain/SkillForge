import os
import requests
import numpy as np
from numpy.linalg import norm
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import openai
from docx import Document

# Load environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Initialize the OpenAI client
client = OpenAI()
# Example aptitude questions and answers for reference
example_aptitude_qa = """
1. The clock shows 3:15. What is the angle between the hour and the minute hand?
Answer: At 3:00, the hour hand is at 90 degrees. Every minute, it moves by 0.5 degrees. At 3:15, it has moved 15 * 0.5 = 7.5 degrees. The minute hand at 15 minutes is at 90 degrees. The angle between them is 90 - 7.5 = 82.5 degrees.
2. If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?
Answer: This question tests your understanding of rate and efficiency. Each machine takes 5 minutes to make one widget. 100 machines would also take 5 minutes to make 100 widgets, as each machine works independently.
3. You are in a race and overtake the second person. What position are you in now?
Answer: If you overtake the second person, you take their place, and therefore, you are now in second place.
4. If a store reduces the price of an item by 30% and then by 20%, what is the total percentage reduction?
Answer: This question checks your understanding of successive percentage changes. A 30% reduction reduces the price to 70% of its original price, and a further 20% reduction makes it 80% of the reduced price. So, the final price is 0.7×0.8=0.56.
0.7×0.8=0.56 of the original, which is a 44% reduction.
5. A jar has three red balls, four green balls, and five blue balls. What is the probability of drawing a red ball?
Answer: Total balls = 12 (3 red, 4 green, 5 blue). Probability of drawing a red ball = Number of red balls / Total number of balls = 3/12 = 1/4.
6. If the day after tomorrow is a Wednesday, what day was it three days before the day before yesterday?
Answer: If the day after tomorrow is Wednesday, then today is Monday. The day before yesterday was Saturday, so three days before that was Wednesday.
7. If the probability of an event occurring is 0.20, what are the odds against the event?
Odds against an event = (1 - probability of event) / probability of event. Here, it is (1 - 0.20) / 0.20 = 4/1 or 4:1.
8. In a certain code, 'COMPUTER' is written as 'PMOCTUER'. How would 'KEYBOARD' be written in that code?
Answer: This question tests pattern recognition. In the code, the letters are rearranged in pairs. So, 'KEYBOARD' would be written as 'EKYABDRO'.
9. If a cube's surface area is 150 square units, what is the length of one of its sides?
Answer: The surface area of a cube = 6 × (side)^2. Thus, (side)^2 = 150/6 = 25. Therefore, the side of the cube = √25 = 5 units.
10. How many digits are there in the number 2^20?
Answer: This is a test of your understanding of logarithms. Logarithm base 10 of 2^20 gives the number of digits. Log10(2^20) ≈ 6.02, so there are 7 digits.
11. If 5 cats catch 5 mice in 5 minutes, how many cats are needed to catch 100 mice in 100 minutes?
Answer: As 5 cats catch 5 mice in 5 minutes, they would catch 100 mice in 100 minutes. Thus, the same 5 cats are needed.
12. In a certain code language, 'DESTINY' is coded as 'ESDITNY'. How would 'PROSPER' be coded in that language?
Answer: The pattern in the code involves moving the second letter to the first position and the third letter to the last position while keeping the rest of the letters in the same order. Applying this to 'PROSPER', the code becomes 'RPOSPRE'.
"""

# Function to generate aptitude questions using OpenAI's GPT-3.5 Turbo
def generate_aptitude_questions():
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a list of 5 aptitude questions similar to the following examples:\n\n{example_aptitude_qa}. No explanatory pretext beforehand at all, just the questions."}
        ]
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500
        )
        generated_text = response.choices[0].message.content.strip()
        questions = generated_text.split('\n')
        return questions
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


# Function to generate aptitude answers using OpenAI's GPT-3.5 Turbo
def generate_aptitude_answers(questions):
    answers = []
    for question in questions:
        try:
            prompt = f"Provide a model answer for the following aptitude question:\n\nQuestion: {question}. Only the final answer and no explanation."
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=500
            )
            answer = response.choices[0].text.strip()
            answers.append(answer)
        except Exception as e:
            print(f"An error occurred while generating answer for question '{question}': {e}")
            answers.append("No answer generated.")
    return answers

def evaluate_aptitude_answers(system_answer, user_answer):
    try:
        system_embedding = get_embedding(system_answer)
        user_embedding = get_embedding(user_answer)
        cosine_sim = np.dot(system_embedding, user_embedding) / (norm(system_embedding) * norm(user_embedding))
        similarity_percentage = (cosine_sim + 1) / 2 * 100
        if similarity_percentage < 75:  # Assuming a threshold for correctness
            print("Your answer is incorrect.")
            #print(f"Correct answer: {system_answer}")
        else:
            print("Your answer is correct.")
        return similarity_percentage
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0



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

# Function to generate technical interview questions using OpenAI's GPT-3.5 Turbo
def generate_technical_questions(domain, job_role):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a list of 5 technical interview questions for a candidate applying for a {job_role} role in the {domain} domain. Do not include any explanatory text, just the questions."}
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

# Function to generate answers for technical questions using OpenAI's GPT-3.5 Turbo
def generate_technical_answers(domain, job_role, questions):
    answers = []
    for question in questions:
        try:
            prompt = f"Provide a model answer for the following technical interview question for a {job_role} role in the {domain} domain:\n\nQuestion: {question}"
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=500
            )
            answer = response.choices[0].text.strip()
            answers.append(answer)
        except Exception as e:
            print(f"An error occurred while generating answer for question '{question}': {e}")
            answers.append("No answer generated.")
    return answers

# Function to generate HR interview questions using OpenAI's GPT-3.5 Turbo
def generate_hr_questions():
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Generate a list of 5 HR interview questions. Do not include any explanatory pretext, just the questions."}
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

# Function to provide feedback on HR answers using OpenAI's GPT-3.5 Turbo
def provide_hr_feedback(question, user_answer):
    try:
        prompt = f"Provide feedback and suggest improvements for the following HR interview question and answer:\n\nQuestion: {question}\n\nAnswer: {user_answer}"
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500
        )
        feedback = response.choices[0].text.strip()
        return feedback
    except Exception as e:
        print(f"An error occurred while providing feedback for question '{question}': {e}")
        return "No feedback generated."

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

def main():
    print("Virtual Interview Bot")
    
    domain = input("Enter the domain: ")
    job_role = input("Enter the job role: ")
    
    # Aptitude Section
    print("\nAptitude Section")
    aptitude_questions = generate_aptitude_questions()
    
    for question in aptitude_questions:
        print(f"**Question:** {question}")
        user_answer = input("Your answer: ")
        system_answer = generate_aptitude_answers([question])[0]
        evaluate_aptitude_answers(system_answer, user_answer)
    
    # Technical Section
    print("\nTechnical Section")
    technical_questions = generate_technical_questions(domain, job_role)
    technical_answers = generate_technical_answers(domain, job_role, technical_questions)
    for question, system_answer in zip(technical_questions, technical_answers):
        print(f"**Question:** {question}")
        user_answer = input(f"Your answer to '{question}': ")
        evaluate_student_answer_advanced(system_answer, user_answer)
    
    # HR Section
    print("\nHR Section")
    hr_questions = generate_hr_questions()
    for question in hr_questions:
        print(f"**Question:** {question}")
        user_answer = input(f"Your answer to '{question}': ")
        feedback = provide_hr_feedback(question, user_answer)
        print(f"Feedback: {feedback}")

if __name__ == "__main__":
    main()
