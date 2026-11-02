from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import List

llm = ChatOllama(model="llama3.2:latest")

class Book(BaseModel):
    name: str = Field(description="Book's Name")
    author: str = Field(description="Book's Author")
    publication_year: int = Field(description="The year the book was first published")


# structured_llm = llm.with_structured_output(Book)

# response = structured_llm.invoke(
#     "Suggest a well known sci-fi book"
# )

# print(response)

class BookCollection(BaseModel):
    books: List[Book] = Field(description="a list containing requested books")

structured_llm = llm.with_structured_output(BookCollection)

response = structured_llm.invoke(
    "Suggest 3 well known sci-fi books"
)

print(response.books)