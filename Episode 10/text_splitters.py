from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 25,
    chunk_overlap = 15

)

chunks = splitter.split_documents(docs)

print(chunks[:5])