import ollama

messages = [{"role":"system", "content":"You are a freindly assistant."}]
model_name = "llama3.2:latest"
while True:
    user_prompt = input("You: ")
    if user_prompt=="bye":
        break
    user_role = {"role":"user", "content":user_prompt}

    messages.append(user_role)

    response = ollama.chat(model = model_name, messages=messages)
    response = response.message.content

    print("Assistant:", response)
    assistant_role = {"role":"assistant", "content":response}
    messages.append(assistant_role)
