import ollama

messages = [
    {
        "role": "system",
        "content": "You are a strict university professor. Answer in three formal bullet points"
    },
    {
        "role": "user",
        "content": "What is AI?"
    }
]

model_name = "llama3.2:latest"

response = ollama.chat(model = model_name, messages = messages)

print(response)