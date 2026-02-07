import os
from dotenv import load_dotenv
load_dotenv()

from pageindex.utils import ChatGPT_API, OPENAI_BASE_URL, CHATGPT_API_KEY

print(f"API Key: {CHATGPT_API_KEY[:20]}...")
print(f"Base URL: {OPENAI_BASE_URL}")

model = "glm-4.6v"
prompt = "Return only JSON: {\"status\": \"ok\"}"

print(f"\nTesting with model: {model}")
print("Calling API...")

try:
    response = ChatGPT_API(model=model, prompt=prompt)
    print(f"\nResponse:\n{response}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
