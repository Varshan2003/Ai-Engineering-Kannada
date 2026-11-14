from langchain_ollama import OllamaEmbeddings


docs = [
    "Machine Learning is the backbone of modern AI applications.",
    "Natural Language Processing enables computers to understand human language.",
    "Deep Learning techniques have revolutionized image and speech recognition.",
    "AI Engineeering involves designing algorithms that can learn from data.",
]

embedding_model = OllamaEmbeddings(model="embeddinggemma-2:740m")

vector_embeddings = embedding_model.embed_documents(docs)

print(len(vector_embeddings[0]))