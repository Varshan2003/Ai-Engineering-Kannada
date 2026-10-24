from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly {subject} teacher. Explain simply in under 80 words, with one real-life example."),
    ("user", "{question}")
])

prompt = prompt_template.invoke({"subject": "Physics",
                                "question": "What is Gravity"}
                                )


model_name = "llama3.2:latest"

llm = ChatOllama(model=model_name)

response = llm.invoke(prompt)

parser = StrOutputParser()

response = parser.invoke(response)

print(response)