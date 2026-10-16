# Episode 2 — Notes: Running Local AI with Ollama

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [first_program.py](first_program.py) | A plain Python program (sanity check that Python works) |
| [first_ai_program.py](first_ai_program.py) | One-shot text generation with `ollama.generate()` |
| [roles.py](roles.py) | Message **roles** (`system`, `user`) with `ollama.chat()` |
| [chat_bot.py](chat_bot.py) | A chatbot loop that keeps conversation **history** |

---

## 1. What is Ollama?

**Ollama** is a free tool that lets you download and run Large Language Models (LLMs) such as Llama, Mistral, Gemma and Qwen **on your own computer**.

- **Local** — prompts and answers stay on your machine; no internet needed after the model is downloaded.
- **No API key, no cost per request.**
- It runs a small background **server** at `http://localhost:11434`. Your Python code talks to that server through the `ollama` Python library.

```
Your Python code  ──►  ollama (Python library)  ──►  Ollama server (localhost:11434)  ──►  Model (llama3.2)
```

---

## 2. Ollama Installation Steps

### Step 1 — Install the Ollama app

**macOS**
1. Go to <https://ollama.com/download> and download the macOS app.
2. Unzip it and drag **Ollama.app** into the **Applications** folder.
3. Open it once. A llama icon appears in the menu bar — this means the server is running.

   *Alternative (Homebrew):* `brew install ollama` and then `ollama serve` to start the server.

**Windows**
1. Download `OllamaSetup.exe` from <https://ollama.com/download>.
2. Run the installer. Ollama starts automatically in the background (system tray).

**Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2 — Check the installation
Open a terminal and run:
```bash
ollama --version
```

### Step 3 — Download (pull) a model
The programs in this folder use **Llama 3.2** (about 2 GB, a 3B-parameter model):
```bash
ollama pull llama3.2
```
> `llama3.2` and `llama3.2:latest` mean the same thing. The part after `:` is the **tag** (version/size). Without a tag, `latest` is used.

### Step 4 — Try the model in the terminal
```bash
ollama run llama3.2
```
Type a question, and type `/bye` to exit.

### Step 5 — Install the Python library
```bash
pip install ollama
```
(Use `pip3` on macOS if `pip` isn't found. A virtual environment is recommended: `python3 -m venv .venv && source .venv/bin/activate`.)

### Step 6 — Run the programs
```bash
python3 first_ai_program.py
python3 roles.py
python3 chat_bot.py
```

### Useful Ollama commands

| Command | Purpose |
|---------|---------|
| `ollama list` | Show models downloaded on your machine |
| `ollama pull <model>` | Download a model |
| `ollama run <model>` | Chat with a model in the terminal |
| `ollama rm <model>` | Delete a model to free disk space |
| `ollama ps` | Show models currently loaded in memory |
| `ollama serve` | Start the server manually (if the app isn't running) |

### Common errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'ollama'` | Run `pip install ollama` in the same Python environment you use to run the script |
| `Connection refused` / `Failed to connect to Ollama` | The server isn't running — open the Ollama app or run `ollama serve` |
| `model "llama3.2:latest" not found` | Run `ollama pull llama3.2` |

---

## 3. `generate()` — one-shot prompting

Used in [first_ai_program.py](first_ai_program.py):

```python
response = ollama.generate(model=model_name, prompt=prompt)
print(response.response)
```

- You send **one prompt string**, you get **one answer**.
- The model has **no memory** — every call starts fresh.
- The answer text is in `response.response`.
- Good for single tasks: summarise this, translate this, explain this in one line.

---

## 4. `chat()` and Message Roles

`ollama.chat()` takes a **list of messages** instead of a single string. Each message is a dictionary with two keys:

```python
{"role": "<who is speaking>", "content": "<what they said>"}
```

### The three roles

| Role | Who writes it | Purpose | Example |
|------|---------------|---------|---------|
| `system` | The developer | Sets the AI's **personality, rules, tone and output format**. Usually the first message. The end user normally never sees it. | `"You are a strict university professor. Answer in three formal bullet points"` |
| `user` | The human | The question or instruction. | `"What is AI?"` |
| `assistant` | The model | The AI's previous replies. We add these back into the list so the model remembers what it said. | `"AI is the simulation of human intelligence..."` |

### Each role in simple words

**1. `system`: the rules**
- Written by **you, the developer**, before the conversation starts.
- Sets the AI's personality, tone, rules and answer format.
- Usually first in the list, and only once. The end user doesn't see it, but it shapes every answer.

**2. `user`: the question**
- Written by **the person using the app**.
- The actual question or instruction. A new `user` message is added every time the user types something.

**3. `assistant`: the AI's past answers**
- Written by **the model**. Your code adds its replies back into the list.
- Gives the AI memory of what it already said. The model itself is *stateless*, so without these messages it forgets its earlier answers (see [section 5](#5-building-a-chatbot-with-memory--chat_botpy)).

### Analogy

| Role | Who writes it | Analogy |
|------|---------------|---------|
| `system` | Developer | The job description given to an employee |
| `user` | Human | The customer's question |
| `assistant` | AI | The employee's earlier replies, kept on record |

### Example — [roles.py](roles.py)

```python
messages = [
    {"role": "system", "content": "You are a strict university professor. Answer in three formal bullet points"},
    {"role": "user",   "content": "What is AI?"}
]
response = ollama.chat(model=model_name, messages=messages)
```

- The **system** message changes *how* the model answers — try changing it to "You are a pirate" or "Explain like I'm 5" and run again; the same question gets a very different answer.
- `print(response)` prints the **whole response object** (model name, timings, token counts, etc.). To print only the answer text use:
  ```python
  print(response.message.content)
  ```

### `generate()` vs `chat()`

| | `generate()` | `chat()` |
|---|---|---|
| Input | One `prompt` string | A list of `messages` with roles |
| Roles / system prompt | Not structured (there is an optional `system=` argument) | Built in |
| Memory | None | Yes — if you keep and resend the message history |
| Read the answer | `response.response` | `response.message.content` |
| Best for | One-off tasks | Conversations, chatbots |

---

## 5. Building a Chatbot with Memory — [chat_bot.py](chat_bot.py)

### Key idea: LLMs are *stateless*
The model does **not** remember anything between calls. A chatbot "remembers" only because **we send the entire conversation history every time**.

### How the program works

```python
messages = [{"role": "system", "content": "You are a friendly assistant."}]   # 1. start with the system role

while True:                                                                   # 2. loop forever
    user_prompt = input("You: ")                                              # 3. read user input
    if user_prompt == "bye":                                                  # 4. exit condition
        break

    messages.append({"role": "user", "content": user_prompt})                 # 5. add user message to history

    response = ollama.chat(model=model_name, messages=messages)               # 6. send FULL history
    response = response.message.content                                       # 7. extract the text

    print("Assistant:", response)
    messages.append({"role": "assistant", "content": response})               # 8. add AI reply to history
```

### How the `messages` list grows

```
Turn 1:  [system, user1]                                  → model replies assistant1
Turn 2:  [system, user1, assistant1, user2]               → model replies assistant2
Turn 3:  [system, user1, assistant1, user2, assistant2, user3] → ...
```

So if you say *"My name is Varshan"* in turn 1 and ask *"What is my name?"* in turn 2, the model can answer because turn 1 is still in the list.

**Experiment:** comment out step 8 (`messages.append(assistant_role)`) — the bot will lose track of its own previous answers.

### Things to know
- **Context window:** every model has a limit on how many tokens it can read at once. Very long chats eventually get too big; real apps trim or summarise old messages.
- **Speed:** the longer the history, the more the model has to read, so replies get slightly slower.
- `user_prompt == "bye"` is case-sensitive — `"Bye"` won't exit. `user_prompt.lower().strip() == "bye"` is more forgiving.

---

## 6. Quick Glossary

| Term | Meaning |
|------|---------|
| **LLM** | Large Language Model — an AI trained on huge amounts of text that predicts the next word (token). |
| **Model** | The trained "brain" file, e.g. `llama3.2`. |
| **Tag** | Version/size label after `:` — e.g. `llama3.2:latest`, `llama3.2:1b`. |
| **Parameters** | Numbers learned during training; more parameters (e.g. 3B = 3 billion) usually means smarter but slower and bigger. |
| **Prompt** | The text/instruction you give the model. |
| **System prompt** | Hidden instructions that set the model's behaviour. |
| **Token** | A chunk of text (roughly ¾ of a word) that models read and write. |
| **Context window** | Maximum number of tokens the model can consider at once. |
| **Stateless** | The model keeps no memory between calls; history must be resent. |
| **Inference** | Running a trained model to get an answer. |
