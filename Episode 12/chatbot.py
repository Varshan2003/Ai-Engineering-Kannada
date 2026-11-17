import os
from dotenv import load_dotenv

from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Document Loading
loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")
docs = loader.load()
# print(docs[:2])

#Document Splitting
full_text = "\n".join(doc.page_content for doc in docs)
# print(docs[:1000])
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)
chunks = splitter.create_documents([full_text])
# print(chunks[:3])
# print(len(chunks))

embedding_model = OllamaEmbeddings(
    model="embeddinggemma-2:740m"
)

vector_store = Chroma.from_documents(
    embedding=embedding_model,
    documents=chunks,
    persist_directory="VectorStore"
)

prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant for Kaveri Hospital.\n"
    "Answer the question using ONLY the context below.\n"
    "If the answer is not in the context, say \"I don't know based on the document.\"\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)

parser = StrOutputParser()

aws_bedrock_api_key = os.getenv("aws_api_key")
llm_model = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=aws_bedrock_api_key
)

rag_chain = prompt | llm_model | parser

while True:
    query = input("You: ")
    relevant_docs = vector_store.similarity_search(query=query, k=4)
    response = rag_chain.invoke({"context": relevant_docs, "question": query})
    print(f"Assistant: {response}\n")
