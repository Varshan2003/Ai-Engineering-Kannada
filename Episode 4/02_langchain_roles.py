from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    ("system", "You are a funny Bengaluru auto driver. Reply in one line."),
    HumanMessage("What is AI?")
]

model_name = "llama3.2:latest"

llm = ChatOllama(model=model_name)

response = llm.invoke(messages)

print(response.content)