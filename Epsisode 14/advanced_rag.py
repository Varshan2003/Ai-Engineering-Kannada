import os
from dotenv import load_dotenv

from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient
from sentence_transformers import CrossEncoder

load_dotenv()

embedding_model = OllamaEmbeddings(
    model="embeddinggemma-2:740m"
)
sparrse_model = FastEmbedSparse(model_name="Qdrant/bm25")

if os.path.exists("VectorStore"):
    print("Vector Store already available!")
    vector_store = QdrantVectorStore(
        client = QdrantClient(path = "QdrantStore"),
        embedding=embedding_model,
        sparse_embedding=sparrse_model,
        collection_name = "kaveri_hospital",
        retrieval_mode=RetrievalMode.HYBRID
    )
else:
    loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")
    docs = loader.load()
    pages = {}
    for doc in docs:
        page = doc.metadata.get("page_number", 0)
        pages[page] = pages.get(page, "") + doc.page_content + "\n"

    docs = [Document(page_content=page_content, metadata = {"page_number": page_number}) for page_number, page_content in pages.items()]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200
    )
    chunks = splitter.split_documents(docs)


    vector_store = QdrantVectorStore.from_documents(
        path = "QdrantStore",
        embedding=embedding_model,
        sparse_embedding=sparrse_model,
        collection_name = "kaveri_hospital",
        documents=chunks,
        retrieval_mode=RetrievalMode.HYBRID
    )

rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the user's question so it makes sense without the chat history. "
               "Replace words like he, she, it and that with what they refer to. "
               "Do NOT answer it. Return only the question."),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant for Kaveri Hospital.\n"
               "Answer the question using ONLY the context below.\n"
               "If the answer is not in the context, say \"I don't know based on the document.\"\n"
               "After every fact, cite the page it came from, like this: [page 3]\n\n"
               "Context:\n{context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])

parser = StrOutputParser()

aws_bedrock_api_key = os.getenv("aws_api_key")
llm_model = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=aws_bedrock_api_key
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(question, docs, top_n=4):
    scores = reranker.predict([(question, doc.page_content) for doc in docs])
    ranked = sorted(zip(docs, scores), key=lambda pair: pair[1], reverse=True)
    return [doc for doc, score in ranked[:top_n]]


rewrite_chain = rewrite_prompt | llm_model | parser
answer_chain = answer_prompt | llm_model | parser
chat_history = []
while True:
    query = input("You: ")
    if chat_history:
        search_query = rewrite_chain.invoke({"chat_history": chat_history, "question": query})
    else:
        search_query = query
    candidates = vector_store.similarity_search(query=search_query, k=25)

    relevant_docs = rerank(question = search_query, docs = candidates)
    context = ""
    for doc in relevant_docs:
        page_number = doc.metadata.get("page_number", 0)
        context += f"[page {page_number}] \n {doc.page_content} \n\n"
    response = ""
    for chunk in answer_chain.stream({"context": context, "chat_history" : chat_history, "question": search_query}):
        print(chunk, end = "", flush=True)
        response+=chunk
    chat_history.append(HumanMessage(query))
    chat_history.append(AIMessage(response))
    print(f"Assistant: {response}\n")
