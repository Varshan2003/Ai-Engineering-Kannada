# Episode 6 — Notes: RunnableSequence, RunnableParallel and RunnablePassthrough

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [01_runnable_sequence.py](01_runnable_sequence.py) | The chain from Episode 5, and what `\|` really builds: a `RunnableSequence` |
| [02_runnable_paralle.py](02_runnable_paralle.py) | Running **three chains on the same input** with `RunnableParallel` and getting back a dictionary |
| [03_runnable_passthrough.py](03_runnable_passthrough.py) | Feeding one chain's answer into a second chain, while **keeping the original input**, with `RunnablePassthrough.assign()` |

Everything runs on the same setup as Episodes 4 and 5: Ollama, `llama3.2` and LangChain's `ChatOllama`. If that isn't working yet, see [Episode 2 notes](<../Episode 2/NOTES.md>) for Ollama, and install LangChain's Ollama package:

```bash
pip install langchain-ollama
```

(`langchain-core`, which has `RunnableSequence`, `RunnableParallel` and `RunnablePassthrough`, is installed along with it.)

---

## 1. Quick Recap from Episode 5

- A **Runnable** is any LangChain object with `.invoke()`, `.stream()` and `.batch()`. Prompt templates, chat models and output parsers are all Runnables.
- We joined them with `|` to make a **chain**: `prompt_template | llm | parser`.
- The output of each step becomes the input of the next step.

So far our chains have been a **straight line**: one input in, one answer out. This episode shows two new shapes:

```
Sequence (Section 2)      Parallel (Section 3)            Passthrough (Section 4)

     input                       input                           {question}
       │                  ┌────────┼────────┐                        │
       ▼                  ▼        ▼        ▼                  ┌─────┴──────┐
     step 1            chain_1  chain_2  chain_3               │            ▼
       │                  │        │        │                  │      explain_chain
       ▼                  └────────┼────────┘                  │            │
     step 2                        ▼                           └─────┬──────┘
       │              {explain, hashtags, quiz}                      ▼
       ▼                                                    {question, answer}
     output                                                          │
                                                                     ▼
                                                               rate the answer
```

---

## 2. `RunnableSequence` — [01_runnable_sequence.py](01_runnable_sequence.py)

When you write

```python
chain = prompt_template | llm | parser
```

LangChain builds a **`RunnableSequence`** for you. You can also build it yourself, which is the commented-out line in the file:

```python
from langchain_core.runnables import RunnableSequence

chain = RunnableSequence(prompt_template, llm, parser)
```

Both lines make **exactly the same chain**. Try it:

```python
chain = prompt_template | llm | parser
print(type(chain))   # <class 'langchain_core.runnables.base.RunnableSequence'>
```

| | `a \| b \| c` | `RunnableSequence(a, b, c)` |
|---|---|---|
| Result | A `RunnableSequence` | A `RunnableSequence` |
| Style | LCEL (LangChain Expression Language) | Plain Python class |
| Commonly used? | Yes, this is what you'll see in most code | Rarely; useful to understand what `\|` does |

The rest of the program is the same as Episode 5: `.stream()` prints the answer as it's being written.

> **Takeaway:** `|` isn't magic. It's a short way of writing `RunnableSequence(...)`, and since a sequence is also a Runnable, it can be used inside bigger chains.

---

## 3. `RunnableParallel` — [02_runnable_paralle.py](02_runnable_paralle.py)

Sometimes you want **several different things** from the **same input**. For one article about Mysuru Dasara, we want:

1. a 2-line explanation
2. 3 hashtags
3. 1 quiz question

### Step 1: three small chains

```python
chain_1 = ChatPromptTemplate.from_template("explain in 2 lines: \n {text}")      | llm | parser
chain_2 = ChatPromptTemplate.from_template("Write 3 hashtags about: \n {text}")  | llm | parser
chain_3 = ChatPromptTemplate.from_template("Give 1 quiz question about: \n {text}") | llm | parser
```

`ChatPromptTemplate.from_template(...)` is a shortcut for a template with **one user message** and no system message. It's the same as:

```python
ChatPromptTemplate.from_messages([("user", "explain in 2 lines: \n {text}")])
```

### Step 2: run them all together

```python
parallel = RunnableParallel(explain=chain_1, hashtags=chain_2, quiz=chain_3)

results = parallel.invoke({"text": article})
```

- **Every** chain gets the **same input**: `{"text": article}`.
- The chains are started **at the same time** instead of one after the other. LangChain runs them on separate threads.
- The result is a **dictionary**. The keys are the names you chose (`explain`, `hashtags`, `quiz`) and the values are each chain's answer:

```python
{
    "explain":  "The Mysuru Dasara is a 10-day festival ...",
    "hashtags": "#MysuruDasara #Karnataka #JambooSavari",
    "quiz":     "How many bulbs light up the Mysuru Palace during Dasara?"
}
```

That's why the program can loop over it:

```python
for key, value in results.items():
    print(f"{key}: \n {value}")
```

> **Analogy:** a teacher hands the same article to three students. One writes a summary, one writes hashtags, one writes a quiz question. They all work at the same time, and the teacher collects three answers at the end.

### Is it really faster?

LangChain sends the three requests at once. Whether the model **works on them at the same time** depends on how much your computer and Ollama can handle at once; if it can't, Ollama queues them and handles them one by one. On a cloud API (like OpenAI or Claude) the requests usually do run side by side, so three calls take about as long as one.

**Experiment:** wrap the `invoke` with a timer and compare it with calling `chain_1`, `chain_2` and `chain_3` one after another:

```python
import time
start = time.time()
results = parallel.invoke({"text": article})
print(f"Took {time.time() - start:.1f} seconds")
```

### A shortcut: a plain dictionary

Inside a chain, a plain Python dictionary of Runnables is turned into a `RunnableParallel` automatically. These two mean the same thing:

```python
RunnableParallel(explain=chain_1, hashtags=chain_2)
{"explain": chain_1, "hashtags": chain_2}          # only when used with | in a chain
```

You'll see this dictionary style a lot in RAG code later in the course.

---

## 4. `RunnablePassthrough` — [03_runnable_passthrough.py](03_runnable_passthrough.py)

This program uses **two** steps:

1. **Explain**: answer a question in 3 simple lines.
2. **Rate**: judge how clear that answer is for a 15-year-old.

The problem: the rating prompt needs **both** the original `question` **and** the `answer`:

```python
rate_prompt_template = ChatPromptTemplate.from_template(
    "Question: {question}\nAnswer: {answer}\n\n"
    "Rate how clear the answer is for a 15-year-old, from 1 to 10, with one line of feedback.")
```

If we simply wrote `explain_chain | rate_prompt_template`, the rate template would only receive the answer string, and the `question` would be lost.

### `RunnablePassthrough()` on its own

`RunnablePassthrough()` is a Runnable that **does nothing**: whatever goes in comes out unchanged.

```python
RunnablePassthrough().invoke({"question": "What is gravity"})
# {'question': 'What is gravity'}
```

On its own that's not very useful. Its `.assign()` method is where it helps.

### `RunnablePassthrough.assign(...)`

```python
feedback_chain = RunnablePassthrough.assign(answer=explain_chain) | rate_prompt_template | llm | parser
```

`.assign(answer=explain_chain)` means: *keep the input dictionary as it is, run `explain_chain` on it, and **add** the result under a new key `answer`.*

```
{"question": "What is gravity"}
              │
              ▼
RunnablePassthrough.assign(answer=explain_chain)
              │
              ▼
{"question": "What is gravity",
 "answer":   "Gravity is a force that pulls things ..."}
              │
              ▼
rate_prompt_template | llm | parser
              │
              ▼
"8/10 — Clear and simple, but an example would help."
```

- The original keys (`question`) are **passed through** untouched; that's where the name comes from.
- The new key (`answer`) is **added** next to them.
- Now the rate template has both `{question}` and `{answer}`, so it can be filled in.

> **Analogy:** a file moving between two desks. The first clerk doesn't replace what's in the file; they **add** their page to it and pass the whole file on.

### `.assign()` vs `RunnableParallel`

| | `RunnableParallel(answer=...)` | `RunnablePassthrough.assign(answer=...)` |
|---|---|---|
| Output keys | Only the keys you name | The **original keys** + the new ones |
| Use it when | You want several new results | You want to **add** to the input and pass it all on |

**Experiment:** uncomment the line `# print(explain_chain.invoke({"question": "What is gravity"}))` to see the explanation on its own, then compare it with the rating.

**Experiment:** add a step that prints the dictionary in the middle:

```python
step = RunnablePassthrough.assign(answer=explain_chain)
print(step.invoke({"question": "What is gravity"}))
```

---

## 5. Running the Programs

```bash
cd "Episode 6"
python3 01_runnable_sequence.py
python3 02_runnable_paralle.py
python3 03_runnable_passthrough.py
```

Make sure Ollama is running and the model is downloaded (`ollama pull llama3.2`).

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_ollama'` | LangChain's Ollama package isn't installed | `pip install langchain-ollama` |
| `KeyError` / "missing variables" | A template variable wasn't in the input dictionary | Check every `{variable}` the template uses; in program 3, `.assign()` is what adds `{answer}` |
| `ConnectionError` / connection refused | The Ollama server isn't running | Open the Ollama app, or run `ollama serve` |
| `model "llama3.2:latest" not found` | The model isn't downloaded | `ollama pull llama3.2` |

---

## 6. Quick Glossary

| Term | Meaning |
|------|---------|
| **`RunnableSequence`** | Runnables run one after another, each step's output feeding the next. What `a \| b \| c` builds. |
| **`RunnableParallel`** | Runs several Runnables on the **same input** at the same time and returns a dictionary of their outputs. |
| **`RunnablePassthrough`** | A Runnable that returns its input unchanged. |
| **`RunnablePassthrough.assign()`** | Keeps the input dictionary and adds new keys computed by other Runnables. |
| **`ChatPromptTemplate.from_template()`** | A shortcut for a prompt template with a single user message. |
| **LCEL** | LangChain Expression Language: the style of building chains with `\|` (and dictionaries for parallel steps). |
