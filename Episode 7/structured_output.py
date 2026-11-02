from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

llm = ChatOllama(model="llama3.2:latest")


# Problem
text = "Hey, I'm Varshan, I'm 24 years old, you can reach me at varshan.lives@gmail.com"

# response = llm.invoke(f"Extract user's name, age and email id from the text: {text}")
# print(type(response.content))

class UserDetails(BaseModel):
    name: str = Field(description="Complete Name")
    age: int = Field(description="User's Age")
    email: str = Field(description="User Email")


structured_llm = llm.with_structured_output(UserDetails)

response = structured_llm.invoke(f"Extract user's name, age and email id from the text: {text}")

# print(response.name)
# print(response.age)

dis_output = response.model_dump()
print(dis_output)