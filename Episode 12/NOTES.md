# Episode 12 — Notes: RAG Chatbot (Chat with Your PDF)

These notes cover the theory behind the program in this folder:

| File | What it shows |
|------|---------------|
| [chatbot.py](chatbot.py) | A complete **RAG chatbot** that answers questions about the Kaveri Hospital handbook |
| [kaveri-hospital-handbook.pdf](kaveri-hospital-handbook.pdf) | The document the chatbot "knows" about |

Every piece of this program was built in an earlier episode. This episode puts them together:

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │   LOAD   │ ─► │  SPLIT   │ ─► │  EMBED   │ ─► │  STORE   │ ─► │ RETRIEVE │ ─► │ GENERATE │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
  Episode 10      Episode 10      Episode 11      Episode 11      Episode 12      Episodes 5, 8
```

---

## 1. Setup

You need three things:

1. **Ollama running**, with the embedding model from [Episode 11](<../Episode 11/NOTES.md>):

   ```bash
   ollama pull embeddinggemma-2:740m
   ```

2. **Your Bedrock key** in the `.env` file at the repo root (from [Episode 8](<../Episode 8/NOTES.md>)):

   ```
   aws_api_key=your_bedrock_key_here
   ```

3. **The packages** inside your virtual environment:

   ```bash
   source .venv/bin/activate
   pip install -qU langchain-unstructured "unstructured[pdf]" langchain-text-splitters \
                   langchain-ollama langchain-chroma langchain-openai python-dotenv
   ```

| Package | Used for | First seen in |
|---------|----------|---------------|
| `langchain-unstructured` | `UnstructuredLoader`: reads the PDF | Episode 10 |
| `langchain-text-splitters` | `RecursiveCharacterTextSplitter`: cuts text into chunks | Episode 10 |
| `langchain-ollama` | `OllamaEmbeddings`: turns chunks into vectors | Episode 11 |
| `langchain-chroma` | `Chroma`: stores and searches the vectors | Episode 11 |
| `langchain-openai` | `ChatOpenAI`: talks to Kimi on AWS Bedrock | Episode 8 |
| `python-dotenv` | Reads the API key from `.env` | Episode 8 |

---

## 2. The Problem: The LLM Has Never Read Your Document

Ask a normal LLM *"What are the cardiology OPD timings at Kaveri Hospital?"* and one of two things happens:

- It says it doesn't know, because the handbook was never in its training data.
- Worse, it **makes up** an answer that sounds confident (a **hallucination**).

We could paste the whole handbook into every prompt, but:

| Problem | Why it matters |
|---------|----------------|
| **Too long** | Big documents don't fit in the model's context window |
| **Too expensive** | Cloud models charge per token; sending 100 pages per question adds up fast |
| **Worse answers** | Models get distracted when the useful sentence is buried in pages of noise |

---

## 3. The Idea: Retrieval-Augmented Generation (RAG)

**RAG** = before asking the LLM, **retrieve** the few chunks that are relevant to the question, and **augment** (add) them to the prompt. The LLM then **generates** an answer from those chunks.

### Analogy: an open-book exam

A student in an open-book exam doesn't read the whole textbook for every question. They:

1. Read the question.
2. Flip to the 2–3 pages that talk about it (**retrieve**).
3. Write the answer using those pages (**generate**).

The vector store is the book's index. The LLM is the student.

### Two phases

```
 PHASE 1 — INDEXING (once, before chatting)
 ──────────────────────────────────────────
 handbook.pdf ──► load ──► split ──► embed ──► Chroma (VectorStore/)

 PHASE 2 — QUERYING (every question)
 ───────────────────────────────────
 question ──► embed ──► search Chroma ──► top 4 chunks ─┐
     │                                                  ▼
     └──────────────────────────────────────────► prompt ──► LLM ──► answer
```

---

## 4. Walking Through [chatbot.py](chatbot.py)

### Step 1: Load the PDF (Episode 10)

```python
loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")
docs = loader.load()
```

Remember from Episode 10: `UnstructuredLoader` gives **one `Document` per element** (title, paragraph, list item...), not one per page. So `docs` is a long list of small pieces.

### Step 2: Join and split (Episode 10)

```python
full_text = "\n".join(doc.page_content for doc in docs)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([full_text])
```

Why join first? In Episode 10 we saw that the splitter **never joins** Documents, it only cuts big ones. The elements were already tiny, so splitting them directly would leave hundreds of one-line chunks. Joining everything into one string and then splitting gives us **~1000-character chunks**, each with enough context to answer a question.

| Setting | Value | Meaning |
|---------|-------|---------|
| `chunk_size` | 1000 | Each chunk is at most ~1000 characters |
| `chunk_overlap` | 200 | Neighbouring chunks share 200 characters, so a sentence cut at the edge still appears whole in one of them |

> **Trade-off:** joining throws away each element's metadata (like `page_number`). The chunks no longer know which page they came from. Episode 13 brings metadata back for citations.

### Step 3: Embed and store (Episode 11)

```python
embedding_model = OllamaEmbeddings(model="embeddinggemma-2:740m")

vector_store = Chroma.from_documents(
    embedding=embedding_model,
    documents=chunks,
    persist_directory="VectorStore",
)
```

Each chunk becomes a 768-number vector and is saved in the `VectorStore/` folder. We use `from_documents` (not `from_texts`) because `create_documents` returns `Document` objects.

### Step 4: The RAG prompt (Episode 5)

```python
prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant for Kaveri Hospital.\n"
    "Answer the question using ONLY the context below.\n"
    "If the answer is not in the context, say \"I don't know based on the document.\"\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)
```

This prompt is the most important part of RAG. Each line has a job:

| Line | Job |
|------|-----|
| "You are a helpful assistant for Kaveri Hospital." | Sets the role and tone |
| "Answer ... using **ONLY** the context below." | Stops the model from using its own (possibly wrong) knowledge |
| "If the answer is not in the context, say 'I don't know...'" | Gives the model a **safe way out** instead of guessing. This is the main defence against hallucination |
| `{context}` | Filled with the retrieved chunks |
| `{question}` | Filled with the user's question |

### Step 5: The LLM and the chain (Episodes 5, 6, 8)

```python
llm_model = ChatOpenAI(
    model="moonshotai.kimi-k2.5",
    base_url="https://bedrock-mantle.ap-southeast-2.api.aws/v1",
    api_key=os.getenv("aws_api_key"),
)

rag_chain = prompt | llm_model | StrOutputParser()
```

The same `prompt | llm | parser` chain from Episode 5. `StrOutputParser` turns the model's message into a plain string.

Notice the split of work: **embeddings run locally** in Ollama (free, private, fast), while **answers come from a cloud model** (smarter). Any chat model works here. Swap in `ChatOllama(model="llama3.2")` and it runs fully offline.

### Step 6: The chat loop (retrieve + generate)

```python
while True:
    query = input("You: ")
    relevant_docs = vector_store.similarity_search(query=query, k=4)
    response = rag_chain.invoke({"context": relevant_docs, "question": query})
    print(f"Assistant: {response}\n")
```

For every question:

1. `similarity_search(k=4)` finds the **4 chunks closest in meaning** to the question.
2. Those chunks fill `{context}`, the question fills `{question}`.
3. The chain sends the prompt to Kimi and prints the answer.

### Choosing `k`

| `k` | Effect |
|-----|--------|
| Too small (1) | The answer may be spread across two chunks, and one is missed |
| Too large (20) | More tokens, more cost, and irrelevant chunks can confuse the model |
| 3–5 | A good starting point for ~1000-character chunks |

---

## 5. Things to Know About This Version

This program works, but it is a **first version**. These are the rough edges, and how to fix each one.

### 5.1 The context contains raw `Document` objects

`relevant_docs` is a **list of `Document` objects**. When the template fills `{context}`, Python turns that list into text with `str()`, so the model sees something like:

```
[Document(id='3f2a...', metadata={}, page_content='Cardiology OPD: Mon–Wed ...'), Document(...)]
```

The model can usually still read it, but the IDs and brackets are wasted tokens. Better: send only the text.

```python
context = "\n\n".join(doc.page_content for doc in relevant_docs)
response = rag_chain.invoke({"context": context, "question": query})
```

### 5.2 The handbook is re-embedded on every run

`Chroma.from_documents(...)` runs every time the program starts. That means:

- Startup is slow, because every chunk is embedded again.
- As we saw in Episode 11, it **adds** to the existing folder, so after 3 runs every chunk is stored 3 times, and `k=4` can return the **same chunk several times**.

Fix: build the store only if it doesn't exist yet.

```python
if os.path.exists("VectorStore"):
    vector_store = Chroma(persist_directory="VectorStore", embedding_function=embedding_model)
else:
    # load, split, then:
    vector_store = Chroma.from_documents(documents=chunks, embedding=embedding_model,
                                         persist_directory="VectorStore")
```

Until then, delete the `VectorStore/` folder before each run.

### 5.3 No way to quit

`while True` never ends on its own. Press **Ctrl+C**, or add:

```python
if query.strip().lower() in ("exit", "quit"):
    break
```

### 5.4 No memory

Each question is answered on its own. Ask "Who is the cardiologist?" then "What are **his** timings?", and the second search has no idea who "his" is. Chat history with RAG comes in Episode 13.

---

## 6. The LangChain Way: Retriever + `RunnablePassthrough`

In [chatbot.py](chatbot.py), retrieval happens **outside** the chain, in the `while` loop. LangChain lets us put it **inside** the chain, using what we learned in Episode 6.

```python
from langchain_core.runnables import RunnablePassthrough

retriever = vector_store.as_retriever(search_kwargs={"k": 4})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm_model
    | StrOutputParser()
)

rag_chain.invoke("What are the visiting hours?")
```

What happens:

```
            ┌──► retriever ──► format_docs ──► "context"  ─┐
 question ──┤                                              ├──► prompt ──► LLM ──► parser ──► answer
            └──► RunnablePassthrough ────────► "question" ─┘
```

| Piece | What it is |
|-------|-----------|
| `as_retriever()` | Wraps the vector store in a **Runnable**: input a question, output a list of `Document`s |
| `{ ... }` dict | A `RunnableParallel` (Episode 6): runs both branches on the same input |
| `RunnablePassthrough()` | Passes the question through unchanged |
| `format_docs` | Plain function; LangChain wraps it automatically. Also fixes 5.1 |

Now the whole RAG pipeline is **one chain**, and the loop becomes just `rag_chain.invoke(query)`.

---

## 7. Experiments

**Experiment:** ask something that **is** in the handbook, then something that **isn't** (e.g. "Who won the IPL in 2024?"). Do you get "I don't know based on the document."? Now delete the "If the answer is not in the context..." line from the prompt and ask again.

**Experiment:** before calling the chain, print the retrieved chunks:

```python
for d in relevant_docs:
    print("---", d.page_content[:150])
```

When an answer is wrong, check here first. Bad answers usually mean **bad retrieval**, not a bad LLM.

**Experiment:** change `k` to 1 and then to 10. Which questions break with `k=1`?

**Experiment:** change `chunk_size` to 300 and to 3000 (delete `VectorStore/` each time). How do the answers change?

**Experiment:** ask the same question in different words: "When can I visit a patient?" vs "visiting hours". Does retrieval still find the right chunk? That's semantic search from Episode 11 at work.

**Experiment:** apply the fixes from Section 5 and rewrite the chain the LangChain way from Section 6.

**Experiment:** swap `ChatOpenAI` for `ChatOllama(model="llama3.2")`. Now nothing leaves your laptop.

---

## 8. Running the Program

Run it **from inside the folder**, because the PDF path is relative:

```bash
cd "Episode 12"
python3 chatbot.py
```

```
You: What are the OPD timings for cardiology?
Assistant: ...
```

The first run creates a `VectorStore/` folder. Press **Ctrl+C** to quit.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError: kaveri-hospital-handbook.pdf` | Ran from the repo root | `cd "Episode 12"` first |
| `ConnectionError` / `Connection refused` | Ollama isn't running | Open the Ollama app (or `ollama serve`) |
| `model "embeddinggemma-2:740m" not found` | Model not pulled | `ollama pull embeddinggemma-2:740m` |
| `401` / `AuthenticationError` | Missing or wrong `aws_api_key` in `.env` | Check the key name and value (Episode 8) |
| `ImportError` mentioning `pdf` or `unstructured` | PDF extras not installed | `pip install "unstructured[pdf]"` |
| Startup gets slower each run, duplicate chunks | `from_documents` adds to `VectorStore/` every run | Delete `VectorStore/`, or apply fix 5.2 |
| "I don't know" for a question the handbook answers | The right chunk wasn't retrieved | Print the chunks; try a bigger `k` or different `chunk_size` |

---

## 9. Quick Glossary

| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-Augmented Generation: find relevant chunks, add them to the prompt, let the LLM answer from them. |
| **Hallucination** | When an LLM confidently makes up an answer that isn't true. |
| **Indexing** | The one-time step: load → split → embed → store. |
| **Retrieval** | Finding the chunks most similar to the question (`similarity_search`). |
| **Context** | The retrieved chunks pasted into the prompt. |
| **Grounding** | Making the model answer only from the given context, not its own memory. |
| **`k`** | How many chunks to retrieve per question. |
| **Retriever** | A Runnable that takes a question and returns relevant `Document`s (`vector_store.as_retriever()`). |
| **`format_docs`** | A helper that joins retrieved `Document`s into one string for the prompt. |
| **Context window** | The maximum amount of text a model can read in one request. |
