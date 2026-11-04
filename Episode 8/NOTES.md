# Episode 8 — Notes: Using Cloud LLMs (Groq and AWS Bedrock)

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [groq_chat.py](groq_chat.py) | Calling a model hosted on **Groq** with LangChain's `ChatGroq` |
| [aws_chat.py](aws_chat.py) | Calling a model hosted on **AWS Bedrock** through its OpenAI-compatible endpoint, using `ChatOpenAI` |
| [bedrock-models.txt](bedrock-models.txt) | The model IDs you can use in `aws_chat.py` |

The AWS part has more setup, so it has its own detailed notes: **[AWS_BEDROCK_NOTES.md](AWS_BEDROCK_NOTES.md)**.

Install the packages for this episode:

```bash
pip install langchain-groq langchain-openai python-dotenv
```

---

## 1. Quick Recap: Everything So Far Ran on Our Laptop

From Episode 2 to Episode 7, every program used **Ollama** and `llama3.2`, running on our own machine:

```python
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2")
```

That's great for learning: it's free, it works offline, and your data never leaves your computer. But it has limits:

- **Small models only.** A laptop can run a 3B or 8B model. The strong models have tens or hundreds of billions of parameters, and need GPUs costing lakhs of rupees.
- **Speed depends on your hardware.** On an older laptop, answers come slowly.
- **Hard to share.** If you build an app, your users can't use the model running on your laptop.

This episode moves the model **off our laptop and into the cloud**.

---

## 2. Local vs Cloud LLMs

With a cloud LLM, the model runs on a company's servers. Your program sends the prompt over the internet and gets the answer back.

```
Local (Ollama)                         Cloud (Groq / AWS)

your program                           your program
     │                                      │  prompt + API key
     ▼                                      ▼  (over the internet)
Ollama on your laptop                  provider's servers (big GPUs)
     │                                      │
     ▼                                      ▼
  answer                                 answer
```

| | Local (Ollama) | Cloud (Groq, AWS Bedrock, …) |
|---|---|---|
| Where the model runs | Your computer | The provider's servers |
| Model size | Small (fits your RAM) | Small to very large |
| Cost | Free (your electricity) | Free tier, then pay per token |
| Needs internet | No | Yes |
| Needs an API key | No | Yes |
| Your data | Stays on your machine | Sent to the provider |

> **Analogy:** Ollama is cooking at home: free and private, but you're limited to your own kitchen. A cloud LLM is ordering from a restaurant: a much bigger kitchen, but you pay per order and the restaurant sees what you ordered.

---

## 3. API Keys and the `.env` File

A cloud provider needs to know **who is calling**, so it can apply your limits and send you the bill. You prove who you are with an **API key**, a long secret string the provider gives you.

> ⚠️ **An API key is like your ATM PIN.** Anyone who has it can use your account, and you pay for what they use. Never paste it into code, into `requirements.txt`, into a screenshot, or into a GitHub commit.

### Keep keys in a `.env` file

Put your keys in a file named `.env` in the project folder:

```
groq_api_key=gsk_your_key_here
aws_api_key=your_bedrock_key_here
```

Both programs read it the same way:

```python
from dotenv import load_dotenv
import os

load_dotenv()                          # reads .env and loads it into the environment
api_key = os.getenv("groq_api_key")    # gets one value by name
```

- **`load_dotenv()`** comes from the `python-dotenv` package. It reads each `name=value` line in `.env`.
- **`os.getenv("groq_api_key")`** returns the value, or `None` if the name isn't found.
- The code only ever contains the **name** of the key, never the key itself, so the code is safe to share.

### Keep `.env` out of Git

Create a file named `.gitignore` in the project folder with this line:

```
.env
```

Git will then never add `.env` to a commit. If a key does get committed or shared by mistake, deleting it from the file is **not enough**: go to the provider's console, **delete (revoke) that key**, and create a new one.

---

## 4. Groq — [groq_chat.py](groq_chat.py)

**Groq** is a company that runs open models (Llama, Qwen, GPT-OSS and others) on its own chips, built specially to generate text fast. It has a **free tier**, which makes it a good first cloud provider.

### Getting a key

1. Sign up at <https://console.groq.com>.
2. Open **API Keys** and click **Create API Key**.
3. Copy the key (it starts with `gsk_`) into `.env` as `groq_api_key=...`. Groq shows it only once.

### The code

```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=api_key
)

print(llm.invoke("Hi, How are you?").content)
```

Compare it with what we wrote in Episode 4:

```python
llm = ChatOllama(model="llama3.2")
print(llm.invoke("Hi, How are you?").content)
```

Only the **class** and the **model name** changed. You also pass the API key. The `.invoke()` line is exactly the same.

### Choosing a model

Groq model names look like `provider/model`. The list of current models and their free-tier limits is at <https://console.groq.com/docs/rate-limits> (the link is in the code too). Models get added and removed over time, so if a name stops working, pick a new one from that page.

### Rate limits

The free tier limits how much you can use, for example **requests per minute** and **tokens per day**. If you go over, you get a `429 Too Many Requests` error. Wait a minute and try again, or pick a model with higher limits.

---

## 5. AWS Bedrock — [aws_chat.py](aws_chat.py)

**Amazon Bedrock** is AWS's service for using models from many companies (DeepSeek, Mistral, Qwen, Moonshot, OpenAI's open models, and more) with one AWS account.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=api_key
)
```

This might look strange: we're calling an AWS model with an **OpenAI** class. That's because Bedrock offers an endpoint that speaks the same language as OpenAI's API, and LangChain's own AWS package needs a lot more setup for a beginner.

The full explanation, with key setup and region details, is in **[AWS_BEDROCK_NOTES.md](AWS_BEDROCK_NOTES.md)**.

---

## 6. The Big Idea: Only One Line Changes

Every chat model class in LangChain is a **Runnable** (Episode 5), and they all have the same methods: `.invoke()`, `.stream()`, `.batch()`, and `.with_structured_output()` from Episode 7.

```python
llm = ChatOllama(model="llama3.2")                                       # local
llm = ChatGroq(model="qwen/qwen3.8-27b", api_key=...)                    # Groq
llm = ChatOpenAI(model="moonshotai.kimi-k2.5", base_url=..., api_key=...)  # AWS Bedrock
```

Pick **any one** of these lines, and everything we built earlier still works without changes:

```python
chain = prompt_template | llm | StrOutputParser()   # Episode 5
structured_llm = llm.with_structured_output(UserDetails)   # Episode 7
```

> **Takeaway:** your chains, templates and Pydantic models don't care where the model runs. Build and test with Ollama for free, then switch one line to use a bigger cloud model.

---

## 7. Experiments

**Experiment:** ask Groq, Bedrock and your local `llama3.2` the same question. Which answer is best? Which one arrives fastest?

**Experiment:** time each call:

```python
import time

start = time.time()
llm.invoke("Explain photosynthesis in 3 lines")
print(f"{time.time() - start:.2f} seconds")
```

**Experiment:** take [Episode 7's structured_output.py](<../Episode 7/structured_output.py>) and replace `ChatOllama` with `ChatGroq`. Does the bigger model extract the details more accurately?

**Experiment:** stream the answer from Groq, as in Episode 5:

```python
for chunk in llm.stream("Write a short poem about Bengaluru rain"):
    print(chunk.content, end="", flush=True)
```

**Experiment:** remove the key from `.env` (or misspell its name) and run the program. Read the error, so you'll recognise it later.

---

## 8. Running the Programs

```bash
cd "Episode 8"
python3 groq_chat.py
python3 aws_chat.py
```

`load_dotenv()` looks for `.env` in the folder you run the program from and in the folders above it, so a `.env` at the project root works for both.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_groq'` | Package isn't installed | `pip install langchain-groq` |
| `ModuleNotFoundError: No module named 'dotenv'` | Package isn't installed | `pip install python-dotenv` (not `pip install dotenv`) |
| `401 Unauthorized` / `Invalid API Key` | Key is wrong, revoked or expired | Create a new key and update `.env` |
| A key error even though `.env` has the key | `os.getenv()` returned `None`: the name doesn't match, or `.env` wasn't found | Check the spelling of the name in `.env` matches the code exactly, and where you run the program from |
| `404` / `model not found` / `model_decommissioned` | The model name is wrong or no longer offered | Pick a current name from the provider's model list |
| `429 Too Many Requests` | You went over the rate limit | Wait and retry, or use a different model |
| `ConnectionError` / timeout | No internet, or a wrong `base_url` | Check your connection and the URL |

---

## 9. Quick Glossary

| Term | Meaning |
|------|---------|
| **Cloud LLM** | A model that runs on a provider's servers, which you call over the internet. |
| **Provider** | The company that runs the model for you, such as Groq or AWS. |
| **API** | A way for one program to talk to another. Here, the way our code talks to the provider's servers. |
| **API key** | A secret string that proves who is calling the API. Keep it private. |
| **`.env` file** | A file that holds secrets like API keys, kept out of your code and out of Git. |
| **`python-dotenv`** | The library whose `load_dotenv()` reads a `.env` file. |
| **`.gitignore`** | A file listing what Git should never commit, such as `.env`. |
| **Endpoint / `base_url`** | The web address your requests are sent to. |
| **Rate limit** | The most requests or tokens a provider lets you use in a given time. |
| **Free tier** | A limited amount of use a provider gives you without paying. |
| **OpenAI-compatible API** | An API that accepts the same requests as OpenAI's, so OpenAI's client libraries work with it. |
