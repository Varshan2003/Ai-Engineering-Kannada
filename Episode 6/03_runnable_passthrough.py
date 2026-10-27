from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


llm = ChatOllama(model="llama3.2:latest")

parser = StrOutputParser()

question_prompt_template = ChatPromptTemplate.from_template("Explain in simple 3 lines: {question}")

rate_prompt_template = ChatPromptTemplate.from_template(
    "Question: {question}\nAnswer: {answer}\n\n"
    "Rate how clear the answer is for a 15-year-old, from 1 to 10, with one line of feedback.")


explain_chain = question_prompt_template | llm | parser

# print(explain_chain.invoke({"question": "What is gravity"}))

feedback_chain = RunnablePassthrough.assign(answer = explain_chain) | rate_prompt_template | llm | parser

print(feedback_chain.invoke({"question": "What is gravity"}))
