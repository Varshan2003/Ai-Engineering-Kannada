# Episode 8 — AWS Bedrock Notes (Bedrock Mantle)

These notes go with [aws_chat.py](aws_chat.py). For the general ideas of this episode (local vs cloud, API keys, `.env`, Groq), see the main [NOTES.md](NOTES.md) first.

```bash
pip install langchain-openai python-dotenv
```

---

## 1. What Is Amazon Bedrock?

**Amazon Bedrock** is an AWS service that gives you many companies' models through **one AWS account and one bill**. Instead of signing up separately with DeepSeek, Mistral, Qwen, Moonshot and others, you call all of them through AWS.

Look at [bedrock-models.txt](bedrock-models.txt). Each model ID has the form `provider.model-name`:

```
deepseek.v3.2              ← DeepSeek
mistral.ministral-3-8b-instruct   ← Mistral
moonshotai.kimi-k2.5       ← Moonshot AI (the one aws_chat.py uses)
openai.gpt-oss-120b        ← OpenAI's open-weight model
qwen.qwen3-32b             ← Alibaba's Qwen
```

To switch models, you change only the `model=` string in the code.

---

## 2. First: Why Not Use `langchain-aws`?

LangChain has an official AWS package, so that's the obvious first choice:

```bash
pip install langchain-aws
```

```python
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model="<bedrock-model-id>",
    region_name="ap-southeast-2",
)
print(llm.invoke("Hi, How are you?").content)
```

The code is short, but notice what's **missing**: there's no API key in it. `langchain-aws` uses **boto3**, the AWS SDK for Python, and boto3 finds your AWS credentials by itself. Before this code can run, you have to set those up:

1. Install the **AWS CLI**.
2. In the AWS console, open **IAM** and create a user (or role) for your program.
3. Give it permission to call Bedrock models, by attaching an IAM policy.
4. Create an **access key ID** and **secret access key** for that user.
5. Run `aws configure` and enter both keys plus a default region.
6. Make sure the model is available in that region, and use the model ID format the Bedrock Runtime API expects.

Each of these steps can fail with its own error (`NoCredentialsError`, `AccessDeniedException`, `UnrecognizedClientException`, `ValidationException` …), and the messages are hard to understand when you're new to AWS.

| | `langchain-aws` (`ChatBedrockConverse`) | Bedrock Mantle + `ChatOpenAI` (what we use) |
|---|---|---|
| Extra installs | `langchain-aws`, `boto3`, the AWS CLI | `langchain-openai` |
| Credentials | IAM user, access key + secret, `aws configure` | One Bedrock API key in `.env` |
| How you pass the key | Hidden: boto3 finds it | Clear: `api_key=...` in the code |
| Code shape | Only for AWS | Same as any OpenAI-compatible provider |
| When to choose it | Real AWS projects that use IAM roles, or features only the Bedrock Runtime API has | Learning, quick projects, switching between providers |

So `langchain-aws` isn't wrong. For production apps running inside AWS, using IAM roles with it is the more secure choice. It's just too much setup for a first cloud call, and the code it gives you only works with AWS.

---

## 3. What Is Bedrock Mantle?

OpenAI's API became so popular that many providers now accept **the same requests**. Such an API is called **OpenAI-compatible**. If a provider is OpenAI-compatible, OpenAI's client libraries, including LangChain's `ChatOpenAI`, can talk to it. You only change the address they send requests to.

**Bedrock Mantle** is Bedrock's OpenAI-compatible endpoint. Its address is:

```
https://bedrock-mantle.<region>.api.aws/v1
```

```
                        ChatOpenAI(base_url=...)
                                  │
          ┌───────────────────────┼────────────────────────┐
          ▼                       ▼                        ▼
   api.openai.com     bedrock-mantle.<region>.api.aws    other OpenAI-compatible
   (OpenAI's models)  (models on AWS Bedrock)            providers
```

> **Analogy:** think of a phone charger. `ChatOpenAI` is a USB-C cable. More and more devices now have a USB-C port, so one cable charges all of them. Bedrock Mantle is AWS adding a USB-C port.

---

## 4. Getting a Bedrock API Key

Instead of IAM access keys, Bedrock lets you create an **API key** directly:

1. Sign in to the AWS console and open **Amazon Bedrock**.
2. Choose the region you want to use (top right). This course uses **Asia Pacific (Sydney), `ap-southeast-2`**.
3. Open **API keys** in the left menu.
4. Create a key. Bedrock offers two kinds:
   - **Short-term key:** expires after a few hours (12 at most). Safer, but you have to make a new one each session.
   - **Long-term key:** you choose when it expires. Easier for learning; set a short expiry and delete it when you finish.
5. Copy the key into `.env` (AWS shows it only once):

```
aws_api_key=your_bedrock_key_here
```

> ⚠️ Bedrock is a **paid** service, and you pay per token. Calls in this episode cost very little, but keep an eye on **Billing** in the console, set a **budget alert**, and never share your key. Anyone with the key can run up charges on your account.

---

## 5. The Code, Line by Line — [aws_chat.py](aws_chat.py)

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("aws_api_key")
```

This is the same as in [groq_chat.py](groq_chat.py): read the key from `.env` by its name.

```python
llm = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=api_key
)
```

| Argument | What it does |
|----------|--------------|
| `model` | Which model to use. Any ID from [bedrock-models.txt](bedrock-models.txt). |
| `base_url` | **Where** to send requests. Without it, `ChatOpenAI` sends them to OpenAI's own servers, and your AWS key would be rejected. |
| `api_key` | Your Bedrock API key, which proves who is calling. |

```python
print(llm.invoke("Hi, How are you?").content)
```

The same `.invoke()` as every other episode. `llm` is a normal LangChain Runnable, so chains, streaming and `.with_structured_output()` all work with it.

### The region is part of the URL

`ap-southeast-2` inside the URL is the AWS region. To use a different region, change it there, for example `us-east-1`:

```
https://bedrock-mantle.us-east-1.api.aws/v1
```

Not every model is offered in every region, so a model from the list may give a "model not found" error in another region. Make sure your key is valid for the region you pick too: create it in the same region to be safe.

---

## 6. Experiments

**Experiment:** change `model=` to a few IDs from [bedrock-models.txt](bedrock-models.txt), such as `openai.gpt-oss-20b`, `qwen.qwen3-32b` and `deepseek.v3.2`. Ask each the same question and compare the answers.

**Experiment:** ask the model to reply in Kannada. Which models handle Kannada best?

**Experiment:** ask Bedrock which models it offers right now. OpenAI-compatible APIs usually have a `/models` endpoint, and the `openai` package (installed with `langchain-openai`) can read it:

```python
from openai import OpenAI

client = OpenAI(base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1", api_key=api_key)
for model in client.models.list():
    print(model.id)
```

Compare the output with [bedrock-models.txt](bedrock-models.txt). New models may have been added since the list was saved.

**Experiment:** build an Episode 5 chain with the Bedrock model:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Explain {topic} to a 10 year old in 3 lines")
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"topic": "black holes"}))
```

**Experiment:** remove the `base_url` line and run the program. What error do you get, and why?

---

## 7. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_openai'` | Package isn't installed | `pip install langchain-openai` |
| `401` / `Incorrect API key provided` mentioning **openai.com** | `base_url` is missing, so the request went to OpenAI instead of AWS | Add the `base_url=` line |
| `401` / `403` from AWS | The key is wrong, expired (short-term keys expire in hours) or deleted | Create a new key in the Bedrock console and update `.env` |
| `The api_key client option must be set` | `os.getenv("aws_api_key")` returned `None` | Check the name in `.env` matches the code exactly |
| `404` / model not found | The model ID is misspelled, or not offered in this region | Copy the ID exactly from the list, or try another region |
| `429` / throttling | Too many requests in a short time | Wait a bit and retry |
| Connection error / name not resolved | Typo in `base_url`, or no internet | Check the URL: `https://bedrock-mantle.<region>.api.aws/v1` |

---

## 8. Quick Glossary

| Term | Meaning |
|------|---------|
| **AWS** | Amazon Web Services, Amazon's cloud platform. |
| **Amazon Bedrock** | The AWS service for calling models from many companies with one account. |
| **Bedrock Mantle** | Bedrock's OpenAI-compatible endpoint, `bedrock-mantle.<region>.api.aws/v1`. |
| **Region** | A location of AWS data centres, such as `ap-southeast-2` (Sydney) or `us-east-1` (N. Virginia). |
| **Model ID** | The exact name Bedrock uses for a model, such as `moonshotai.kimi-k2.5`. |
| **Bedrock API key** | A key created in the Bedrock console that lets you call Bedrock without IAM access keys. Short-term or long-term. |
| **IAM** | AWS's system for users, roles and permissions. |
| **boto3** | The AWS SDK for Python. `langchain-aws` uses it under the hood. |
| **`langchain-aws`** | LangChain's official AWS package, with classes like `ChatBedrockConverse`. |
| **`ChatOpenAI`** | LangChain's class for OpenAI's API, and for any OpenAI-compatible API when you set `base_url`. |
| **`base_url`** | The address `ChatOpenAI` sends requests to. |
