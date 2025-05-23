import openai
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def llm_match_score(candidate_experiences, job_description):
    # Combine all experience descriptions into one string
    exp_text = ""
    for exp in candidate_experiences:
        exp_text += f"Title: {exp['title']}\nCompany: {exp['company']}\nDates: {exp['start']} to {exp['end']}\nDescription: {exp['description']}\n\n"

    prompt = f'''
You are a job matching assistant. Given the following candidate experience and job description, do the following:
1. Extract the key skills and qualifications from each.
2. Rate the candidate's match to the job on a scale of 0-100%.
3. List the top matching skills and the most important missing skills.
4. Provide a detailed, human-readable justification for your score.

Candidate Experience:
{exp_text}

Job Description:
{job_description}
'''

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content 

# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# try:
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": "Say hello!"}]
#     )
#     print(response.choices[0].message.content)
# except Exception as e:
#     print("Error:", e)