import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()
if __name__ == "__main__":
    print(generate_response("Say hello from Gemini"))
