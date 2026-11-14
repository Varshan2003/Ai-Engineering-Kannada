# Episode 11 — Notes: Vector Embeddings & Vector Stores

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [vector_embeddings.py](vector_embeddings.py) | Turning sentences into **vectors** (lists of numbers) with `OllamaEmbeddings` |
| [vector_store.py](vector_store.py) | Saving those vectors in **Chroma** and finding the sentence closest in meaning to a query |

In [Episode 10](<../Episode 10/NOTES.md>) we **loaded** documents and **split** them into chunks. This episode builds the next two steps: **embed** and **store**.

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │   LOAD   │ ─► │  SPLIT   │ ─► │  EMBED   │ ─► │  STORE   │ ─► │ RETRIEVE │ ─► LLM
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
  Episode 10      Episode 10      Episode 11      Episode 11      Episode 12
```

---

## 1. Setup

This time **Ollama must be running**, because the embedding model runs inside it. Pull the model once:

```bash
ollama pull embeddinggemma-2:740m
```

Then install the packages inside your virtual environment:

```bash
source .venv/bin/activate
pip install -qU langchain-ollama langchain-chroma
```

| Package | What it's for |
|---------|---------------|
| `langchain-ollama` | `OllamaEmbeddings`: talks to the embedding model running in Ollama |
| `langchain-chroma` | LangChain's wrapper around **Chroma**, a vector database that runs on your laptop |

> `embeddinggemma-2` is an **embedding model**, not a chat model. You can't talk to it with `ollama run`. It only turns text into numbers.

---

## 2. The Problem: Computers Don't Understand Meaning

In RAG, the user asks a question and we must find the chunks that answer it. The obvious way is **keyword search**: find chunks that contain the same words.

That breaks quickly:

| Question | Chunk that answers it | Shared words |
|----------|-----------------------|--------------|
| "When can I see the heart doctor?" | "Dr. Rao (Cardiology) — OPD: Mon–Wed, 10 AM–1 PM" | none |
| "How much does a room cost?" | "Ward charges: ₹2,500 per day" | none |

A human sees immediately that these match. Keyword search sees nothing in common. We need a way to compare text by **meaning**, not by spelling.

---

## 3. What Is a Vector Embedding?

A **vector embedding** is a list of numbers that represents the **meaning** of a piece of text.

```python
"Machine Learning is the backbone of modern AI applications."
        │
        ▼  embedding model
[-0.032, -0.0103, 0.0393, 0.0064, 0.0637, ... ]   ← 768 numbers
```

- **Vector** = just a list of numbers, like a point on a map.
- **Embedding** = we "embed" (place) the text at a point in a space of meaning.

The key idea:

> **Texts with similar meaning get vectors that are close together. Texts with different meaning get vectors that are far apart.**

### Analogy: a map of meaning

Imagine a map where every word has a location. On a normal map, Bengaluru and Mysuru are close; Bengaluru and London are far. On a **meaning map**:

```
          ▲  "animal-ness"
          │
   puppy ●  ● dog
          │         ● cat
          │
          │                      ● car
          │                  ● bus
          └──────────────────────────────►  "vehicle-ness"
```

"dog" and "puppy" sit next to each other. "car" is far away. We can now **measure** how related two texts are just by measuring distance.

A real embedding model doesn't use 2 directions, it uses hundreds (768 for `embeddinggemma-2`). We can't draw 768 dimensions, but the maths works exactly the same as on the 2-D map.

### What do the numbers mean?

No single number has a human meaning like "animal-ness". The model **learned** these numbers by reading huge amounts of text and noticing which words and sentences appear in similar situations. The meaning lives in the **pattern** of all 768 numbers together, not in any one of them.

---

## 4. Creating Embeddings — [vector_embeddings.py](vector_embeddings.py)

```python
from langchain_ollama import OllamaEmbeddings

docs = [
    "Machine Learning is the backbone of modern AI applications.",
    "Natural Language Processing enables computers to understand human language.",
    "Deep Learning techniques have revolutionized image and speech recognition.",
    "AI Engineeering involves designing algorithms that can learn from data.",
]

embedding_model = OllamaEmbeddings(model="embeddinggemma-2:740m")

vector_embeddings = embedding_model.embed_documents(docs)

print(len(vector_embeddings[0]))   # 768
```

What you get back:

```python
len(vector_embeddings)        # 4    → one vector per sentence
len(vector_embeddings[0])     # 768  → every vector has 768 numbers
vector_embeddings[0][:5]      # [-0.032, -0.0103, 0.0393, 0.0064, 0.0637]
```

### Every vector has the same length

A 3-word sentence and a 30-word paragraph both become **768 numbers**. The size is fixed by the model, not by the text. That's what lets us compare any two texts.

### Two methods

| Method | Input | Use it for |
|--------|-------|------------|
| `embed_documents(list_of_texts)` | A list of strings | Your chunks, the knowledge you're storing |
| `embed_query(text)` | One string | The user's question at search time |

**Always use the same model for documents and queries.** Vectors from different models live on different "maps", so comparing them is meaningless, like comparing GPS coordinates with pin codes.

---

## 5. Measuring "Closeness": Cosine Similarity

The usual way to compare two embeddings is **cosine similarity**. It looks at the **angle** between two vectors:

```
   same direction          90° apart              opposite
     ──►                     ▲                    ◄──  ──►
     ──►                     │
                             └──►
   similarity ≈ 1         similarity ≈ 0         similarity ≈ -1
   (same meaning)         (unrelated)
```

```python
import math

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
```

Real results from `embeddinggemma-2:740m`:

| Text A | Text B | Cosine similarity |
|--------|--------|-------------------|
| "dog" | "puppy" | **0.968** |
| "dog" | "car" | 0.771 |

And comparing the query **"backbone of modern AI"** with our four sentences:

| Sentence | Similarity |
|----------|-----------|
| Machine Learning is the backbone of modern AI applications. | **0.857** ← best match |
| Deep Learning techniques have revolutionized image and speech recognition. | 0.738 |
| AI Engineeering involves designing algorithms that can learn from data. | 0.732 |
| Natural Language Processing enables computers to understand human language. | 0.709 |

> **Notice:** even unrelated texts score around 0.7, not 0. With real models, the **ranking** matters, not the raw number. Don't pick a fixed cut-off like "above 0.8 means relevant" without testing it on your own data.

`embeddinggemma-2` returns vectors with length 1 (they're **normalized**), so for this model cosine similarity is the same as the plain dot product.

---

## 6. Storing Embeddings: Vector Stores — [vector_store.py](vector_store.py)

Computing similarity against 4 sentences in a loop is fine. Against 1 million chunks, on every question, it's too slow. And we don't want to re-embed the whole handbook every time the program starts.

A **vector store** (vector database) solves both:

1. It **saves** the vectors (and the original text + metadata) to disk.
2. It **searches** them quickly for the nearest neighbours of a query vector.

```python
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embedding_model = OllamaEmbeddings(model="embeddinggemma-2:740m")

vector_store = Chroma.from_texts(
    embedding=embedding_model,
    texts=docs,
    persist_directory="./embeddings",
)

similar_text = vector_store.similarity_search("backbone of modern AI", k=1)
print(similar_text[0].page_content)
# Machine Learning is the backbone of modern AI applications.
```

What happens inside:

```
 from_texts(docs)                         similarity_search("backbone of modern AI", k=1)
 ─────────────────                        ───────────────────────────────────────────────
 each text ──► embed_documents ──► save    query ──► embed_query ──► find nearest k ──► Documents
                                    │                                       ▲
                                    ▼                                       │
                              ./embeddings/  ───────────────────────────────┘
```

| Argument | Meaning |
|----------|---------|
| `embedding` | The model Chroma calls to turn text into vectors (both when storing and when searching) |
| `texts` | Plain strings to store. Use `Chroma.from_documents(chunks, ...)` for Episode 10's `Document` chunks, which keeps their metadata |
| `persist_directory` | Folder where Chroma saves everything. Without it, the store lives only in memory and disappears when the program ends |
| `k` | How many closest results to return |

`similarity_search` returns LangChain `Document` objects, the same kind as in Episode 10, so `.page_content` gives you the text. Use `similarity_search_with_score(query, k=2)` to also see the distance for each result (for Chroma, a **lower** score means **closer**).

### Loading a saved store later

```python
vector_store = Chroma(
    persist_directory="./embeddings",
    embedding_function=embedding_model,
)
vector_store.similarity_search("What is NLP?", k=1)
```

No re-embedding needed, which matters when you have thousands of chunks.

> **Watch out:** `from_texts` **adds** to the existing folder. Run [vector_store.py](vector_store.py) three times and each sentence is stored three times, so `k=3` may return the same sentence three times. Delete the `embeddings/` folder to start fresh.

### Other vector stores you'll hear about

| Store | Where it runs |
|-------|---------------|
| **Chroma** | On your laptop, saved in a folder. Great for learning |
| **FAISS** | A library from Meta; in memory, very fast |
| **pgvector** | Inside a PostgreSQL database |
| **Pinecone, Qdrant, Weaviate, Milvus** | Dedicated vector databases, often hosted in the cloud |

They all do the same two jobs (store vectors, find nearest ones), and LangChain gives them a similar interface.

---

## 7. Experiments

**Experiment:** in [vector_embeddings.py](vector_embeddings.py), print `vector_embeddings[0][:10]`. Then embed a one-word text and a long paragraph. Are the lengths different?

**Experiment:** add the `cosine_similarity` function from Section 5 and compare "doctor" with "physician", "hospital" and "cricket". Does the order match your intuition?

**Experiment:** in [vector_store.py](vector_store.py), search for **"How do computers understand speech?"** with `k=2`. No sentence contains that exact phrase. Which ones come back, and why?

**Experiment:** run [vector_store.py](vector_store.py) twice, then search with `k=4`. Do you see duplicates? Delete the `embeddings/` folder and try again.

**Experiment:** combine with Episode 10. Load the Kaveri hospital handbook, split it, store the chunks with `Chroma.from_documents(chunks, embedding=embedding_model, persist_directory="./handbook_db")`, and ask "When is the cardiologist available?". Print the `page_number` from the result's metadata.

---

## 8. Running the Programs

```bash
cd "Episode 11"
python3 vector_embeddings.py     # prints 768
python3 vector_store.py          # prints the closest sentence
```

`vector_store.py` creates an `embeddings/` folder next to where you run it.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ConnectionError` / `Connection refused` | Ollama isn't running | Open the Ollama app (or `ollama serve`) |
| `model "embeddinggemma-2:740m" not found` | Model not pulled | `ollama pull embeddinggemma-2:740m` |
| `ModuleNotFoundError: No module named 'langchain_chroma'` | Package not installed, or venv not active | `source .venv/bin/activate`, then `pip install langchain-chroma` |
| Same result returned several times | You ran `from_texts` more than once into the same folder | Delete `embeddings/` and run again |
| Strange/irrelevant results after changing models | Old vectors were made with a different model | Delete the store and re-embed with the new model |

---

## 9. Quick Glossary

| Term | Meaning |
|------|---------|
| **Vector** | A list of numbers, like `[0.12, -0.5, 0.33, ...]`. |
| **Embedding** | A vector that represents the meaning of a piece of text. |
| **Embedding model** | A model that turns text into embeddings (here `embeddinggemma-2:740m`). It doesn't generate text. |
| **Dimension** | How many numbers are in each vector (768 here). Fixed by the model. |
| **`embed_documents()`** | Embeds a list of texts (your knowledge). |
| **`embed_query()`** | Embeds one text (the user's question). |
| **Cosine similarity** | A score from -1 to 1 based on the angle between two vectors. Higher = more similar meaning. |
| **Semantic search** | Searching by meaning, using embeddings, instead of by matching keywords. |
| **Vector store** | A database that saves embeddings and quickly finds the ones nearest to a query. |
| **Chroma** | The local vector store used in this episode. |
| **`persist_directory`** | The folder where Chroma saves its data so it survives between runs. |
| **`similarity_search(query, k)`** | Embeds the query and returns the `k` closest stored `Document`s. |
