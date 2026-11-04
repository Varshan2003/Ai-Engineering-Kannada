from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("groq_api_key")

# Models List: https://console.groq.com/docs/rate-limits
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=api_key
)

print(llm.invoke("Hi, How are you?").content)