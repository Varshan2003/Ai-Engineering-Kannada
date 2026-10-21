from langchain_ollama import ChatOllama

model_name = "llama3.2:latest"

llm = ChatOllama(model=model_name)

response = llm.invoke("What is AI?")

print(response)