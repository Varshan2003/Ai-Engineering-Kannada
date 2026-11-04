from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("aws_api_key")

llm = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=api_key
)

print(llm.invoke("Hi, How are you?").content)