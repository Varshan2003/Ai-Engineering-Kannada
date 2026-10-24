# Episode 5 — Notes: Prompt Templates, Runnables and Chains

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [01_prompt_templates.py](01_prompt_templates.py) | A reusable prompt with `{placeholders}`, filled in with `ChatPromptTemplate` |
| [02_runnables.py](02_runnables.py) | Running template → model → `StrOutputParser` one step at a time, each with `.invoke()` |
| [03_sequences.py](03_sequences.py) | Joining the three steps into one **chain** with `|`, and **streaming** the answer |

Everything runs on the same setup as Episode 4: Ollama, `llama3.2` and LangChain's `ChatOllama`. If that isn't working yet, see [Episode 2 notes](<../Episode 2/NOTES.md>) for Ollama, and install LangChain's Ollama package:

```bash
pip install langchain-ollama
```

(`langchain-core`, which has `ChatPromptTemplate` and `StrOutputParser`, is installed along with it.)

---

## 1. Why Prompt Templates?

In Episode 3 we wrote a whole new prompt for every question. In real apps, most of the prompt stays **the same** and only a few parts change:

```
System:  You are a friendly ______ teacher. Explain simply in under 80 words, with one real-life example.
User:    ______
```

A **prompt template** is that prompt with **blanks** (placeholders). You write it once and fill in the blanks for each request.

- The good prompt you designed (role, constraints, format) is written **once**, in one place.
- Your code only supplies the changing parts: here, the `subject` and the `question`.
- The same template works for Physics, Kannada, Maths, anything.

> **Analogy:** a printed application form. The form is the same for everyone; each person only fills in their name and details.

---

## 2. `ChatPromptTemplate` — [01_prompt_templates.py](01_prompt_templates.py)

```python
from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly {subject} teacher. Explain simply in under 80 words, with one real-life example."),
    ("user", "{question}")
])
```

- `from_messages([...])` takes a list of `(role, text)` pairs, the same roles from Episode 2 and Episode 4.
- `"user"` and `"human"` mean the same thing here; both become a `HumanMessage`.
- Anything in **curly braces**, like `{subject}` and `{question}`, is a **variable** to fill in later.

### Filling in the blanks with `.invoke()`

```python
prompt = prompt_template.invoke({"subject": "Kannada",
                                "question": "What is Vyakarana"})
print(prompt)
```

- You pass a **dictionary**: each key is a variable name from the template, each value is what to put there.
- The result is **not a string**. It's a `ChatPromptValue` that holds the finished list of messages:

```
messages=[SystemMessage(content='You are a friendly Kannada teacher. Explain simply ...'),
          HumanMessage(content='What is Vyakarana')]
```

- That is exactly the kind of message list `ChatOllama` accepts, so we pass it straight to the model:

```python
llm = ChatOllama(model="llama3.2:latest")
response = llm.invoke(prompt)
print(response.content)
```

**Experiment:** the file has a commented-out Physics version. Swap between the two and see how one template gives a Physics teacher or a Kannada teacher.

### Template vs f-string

You could do the same with a Python f-string, so why use a template?

| | f-string | `ChatPromptTemplate` |
|---|---|---|
| When it's filled | Immediately, when the line runs | Later, when you call `.invoke()` |
| Output | A plain string | A list of chat messages with roles |
| Reuse | Rewrite it for each input | Define once, invoke with many inputs |
| Fits into a chain with `\|` | No | Yes (see Section 4) |

### Things to know

- **Every variable must be given.** If you forget one, e.g. `invoke({"subject": "Physics"})`, you get a `KeyError` saying `question` is missing.
- **Literal curly braces** (say, a JSON example inside your prompt) must be doubled: `{{` and `}}`. Otherwise LangChain thinks they're variables.

---

## 3. Runnables — [02_runnables.py](02_runnables.py)

This program has **three** objects, and each one is used the same way:

```python
prompt   = prompt_template.invoke({...})   # dict          → ChatPromptValue
response = llm.invoke(prompt)              # ChatPromptValue → AIMessage
response = parser.invoke(response)         # AIMessage     → str
```

In LangChain, anything that has `.invoke()` (and a few related methods) is called a **Runnable**. Prompt templates, chat models and output parsers are all Runnables.

```
 {"subject": ..., "question": ...}
            │
            ▼
   ┌───────────────────┐
   │  prompt_template  │  fills in the blanks
   └───────────────────┘
            │  ChatPromptValue (messages)
            ▼
   ┌───────────────────┐
   │   llm (ChatOllama)│  calls llama3.2
   └───────────────────┘
            │  AIMessage
            ▼
   ┌───────────────────┐
   │  StrOutputParser  │  pulls out the text
   └───────────────────┘
            │  str
            ▼
         print()
```

### Every Runnable has the same methods

| Method | What it does |
|--------|--------------|
| `.invoke(input)` | Run once on one input, return the full output |
| `.stream(input)` | Run once, but give the output back **piece by piece** as it's produced |
| `.batch([input1, input2, ...])` | Run on several inputs and return a list of outputs |

Because they all share this one interface, they can be **plugged into each other**, like LEGO bricks.

### `StrOutputParser`

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
response = parser.invoke(response)
print(response)
```

- `llm.invoke()` returns an **`AIMessage`**, which has the text plus extra details (model name, token counts, timing).
- `StrOutputParser` takes that message and returns **just the text** as a plain Python `str`.
- It does the same job as `response.content` in Episode 4. The difference is that a parser is a Runnable, so it can be the last step of a chain.

**Experiment:** add `print(type(response))` after each of the three steps and watch the type change: `ChatPromptValue` → `AIMessage` → `str`.

---

## 4. Chains with `|` — [03_sequences.py](03_sequences.py)

Doing three `.invoke()` calls by hand works, but each time we pass one step's output to the next ourselves. LangChain lets us join them with the **pipe operator `|`**:

```python
chain = prompt_template | llm | parser
```

- Read `|` as **"then"**: *fill the template, then send it to the model, then pull out the text.*
- The output of the left side automatically becomes the input of the right side.
- The result, `chain`, is a **`RunnableSequence`**, and it is a Runnable too. So it also has `.invoke()`, `.stream()` and `.batch()`.
- This style of building with `|` is called **LCEL** (LangChain Expression Language).

Now one call does all three steps:

```python
answer = chain.invoke({"subject": "Physics", "question": "What is Gravity"})
print(answer)    # a plain string
```

```
Before (02_runnables.py):            After (03_sequences.py):

prompt   = template.invoke(input)    chain  = template | llm | parser
response = llm.invoke(prompt)        answer = chain.invoke(input)
answer   = parser.invoke(response)
```

> **Analogy:** a factory assembly line. Each station does one job and hands the item to the next. You put raw material in at one end and get the finished product out of the other.

### The order matters

Each step must accept what the previous step gives out:

| Chain | Works? | Why |
|-------|--------|-----|
| `prompt_template \| llm \| parser` | ✅ | dict → messages → AIMessage → str |
| `llm \| prompt_template` | ❌ | The template expects a dict of variables, not an `AIMessage` |
| `prompt_template \| parser` | ❌ | There's no model, so there's no answer to parse |

---

## 5. Streaming

```python
for chunk in chain.stream({"subject": "Physics",
                        "question": "What is Gravity"}):
    print(chunk, end="", flush=True)
```

- `.invoke()` waits until the **whole** answer is ready, then returns it.
- `.stream()` gives you the answer **as it's being written**, a few characters (tokens) at a time. This is how ChatGPT-style apps show text appearing word by word.
- A long answer feels much faster, because the user sees the first words almost immediately.
- Streaming works through the whole chain: the parser passes each small piece of text along as it arrives, so every `chunk` is a short string.

### The `print` arguments

| Argument | Why it's needed |
|----------|-----------------|
| `end=""` | By default `print` adds a new line after every call. Without this, each chunk would be on its own line. |
| `flush=True` | Python normally holds printed text in a buffer and shows it later. This makes each chunk appear on screen **right away**. |

**Experiment:** remove `end=""` and run it again, to see what the chunks really look like.

---

## 6. Running the Programs

```bash
cd "Episode 5"
python3 01_prompt_templates.py
python3 02_runnables.py
python3 03_sequences.py
```

Make sure Ollama is running and the model is downloaded (`ollama pull llama3.2`).

**Experiment:** in [03_sequences.py](03_sequences.py), change the input to `{"subject": "Kannada", "question": "What is Sandhi"}`. The chain stays the same; only the input changes.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_ollama'` | LangChain's Ollama package isn't installed | `pip install langchain-ollama` |
| `KeyError` / "missing variables" | A template variable wasn't in the dictionary | Pass every `{variable}` the template uses |
| `ConnectionError` / connection refused | The Ollama server isn't running | Open the Ollama app, or run `ollama serve` |
| `model "llama3.2:latest" not found` | The model isn't downloaded | `ollama pull llama3.2` |

---

## 7. Quick Glossary

| Term | Meaning |
|------|---------|
| **Prompt template** | A prompt with `{placeholders}` that you fill in with different values each time. |
| **`ChatPromptTemplate`** | LangChain's template for chat models; it produces a list of messages with roles. |
| **`ChatPromptValue`** | What a filled-in `ChatPromptTemplate` returns: the finished messages, ready for the model. |
| **Runnable** | Any LangChain object with `.invoke()`, `.stream()` and `.batch()`, e.g. templates, models and parsers. |
| **Output parser** | A Runnable that turns the model's `AIMessage` into something easier to use. |
| **`StrOutputParser`** | An output parser that returns just the text of the answer as a `str`. |
| **Chain / `RunnableSequence`** | Runnables joined with `\|`, where each step's output becomes the next step's input. |
| **LCEL** | LangChain Expression Language: the style of building chains with `\|`. |
| **Streaming** | Getting the model's answer piece by piece as it's generated, instead of all at once. |
