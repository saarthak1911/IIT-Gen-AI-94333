import time
import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

PROMPT = "Explain AI in one sentence"

# ---------------- GROQ ----------------
groq_key = os.getenv("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/chat/completions"

groq_headers = {
    "Authorization": f"Bearer {groq_key}",
    "Content-Type": "application/json"
}

groq_data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": PROMPT}]
}

start = time.time()
groq_res = requests.post(groq_url, headers=groq_headers, json=groq_data)
groq_time = time.time() - start
groq_reply = groq_res.json()["choices"][0]["message"]["content"]

# ---------------- GEMINI ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

start = time.time()
gemini_res = model.generate_content(PROMPT)
gemini_time = time.time() - start
gemini_reply = gemini_res.text

# ---------------- RESULT ----------------
print("\n--- GROQ RESPONSE ---")
print(groq_reply)
print("Time:", round(groq_time, 3), "seconds")

print("\n--- GEMINI RESPONSE ---")
print(gemini_reply)
print("Time:", round(gemini_time, 3), "seconds")