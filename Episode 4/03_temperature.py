from langchain_ollama import ChatOllama

model_name = "llama3.2:latest"


temperatures = [0, 0.5, 2]

for temp in temperatures:
    llm = ChatOllama(model=model_name, temperature=temp)
    response = llm.invoke("What is AI? Reply in one line")
    print(f"Temperature: {temp}, output: {response.content}")