from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


docs = [
    "Machine Learning is the backbone of modern AI applications.",
    "Natural Language Processing enables computers to understand human language.",
    "Deep Learning techniques have revolutionized image and speech recognition.",
    "AI Engineeering involves designing algorithms that can learn from data.",
]

embedding_model = OllamaEmbeddings(model="embeddinggemma-2:740m")

#Storing vector embeddings in a vector store
vector_store = Chroma.from_texts(
    embedding=embedding_model,
    texts=docs,
    persist_directory="./embeddings"
)

similar_text = vector_store.similarity_search("backbone of modern AI", k=1)

print(similar_text[0].page_content)