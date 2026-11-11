from langchain_unstructured import UnstructuredLoader

loader = UnstructuredLoader(web_url="https://docs.langchain.com/oss/python/integrations/document_loaders/unstructured_file")

# loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")
# docs = loader.load()

docs = loader.load()

print(docs[-1])