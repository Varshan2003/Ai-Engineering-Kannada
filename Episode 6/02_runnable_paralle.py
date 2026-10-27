from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

article = """The Mysuru Dasara is a 10-day festival celebrated in Karnataka.
The Mysuru Palace is lit with nearly 100,000 bulbs, and the Jamboo Savari procession
on the last day features decorated elephants."""


llm = ChatOllama(model="llama3.2:latest")
parser = StrOutputParser()

#LCEL
chain_1 = ChatPromptTemplate.from_template("explain in 2 lines: \n {text}")  | llm | parser
chain_2 = ChatPromptTemplate.from_template("Write 3 hashtags about: \n {text}")  | llm | parser
chain_3 = ChatPromptTemplate.from_template("Give 1 quiz question about: \n {text}")  | llm | parser

parallel = RunnableParallel(explain = chain_1, hashtags = chain_2, quiz = chain_3)

results = parallel.invoke({"text": article})

for key, value in results.items():
    print(f"{key}: \n {value}")



