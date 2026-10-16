# AI Engineering in Kannada — Course Curriculum

A beginner-friendly path from "what is AI?" to building RAG apps and AI agents. Every episode builds on the one before it.

**How this course works**

- **Local first.** Episodes run on your own computer with [Ollama](https://ollama.com), so there's no API key and no cost. Hosted APIs come in later, as an option.
- **Understand, then build.** You learn how LLMs work inside (Transformers), call them directly from Python, and then use **LangChain** to build RAG apps faster. Key ideas such as tool calling and the ReAct agent loop are also written by hand once, so nothing feels like magic.
- **Code with every episode.** Each episode folder has notes (`NOTES.md`) and small, runnable Python programs.

**What you need:** a laptop with 8 GB+ RAM, Python 3.10 or newer, and Ollama installed (setup is in [Episode 2](<Episode 2/NOTES.md>)).

---

## Course map

| # | Episode | You will build | Status |
|---|---------|----------------|--------|
| 1 | AI Basics | — | ✅ Done |
| 2 | Running Local AI with Ollama | A chatbot with memory | ✅ Done |
| 3 | Prompt Engineering | A prompt playground | Next |
| 4 | Tool Calling | A bot that uses a calculator and a weather tool | Planned |
| 5 | How LLMs Work: Transformers | A toy attention calculation | Planned |
| 6 | LangChain Basics | The Episode 2 chatbot rebuilt with LangChain | Planned |
| 7 | Embeddings & Semantic Search | Search that understands meaning | Planned |
| 8 | RAG with LangChain | "Chat with your PDF" | Planned |
| 9 | Better RAG | A RAG app with citations and better retrieval | Planned |
| 10 | ReAct Agents from Scratch | An agent that thinks, acts and observes | Planned |

---

## Module 1 — Foundations

### Episode 1 — AI Basics ✅
What AI, machine learning, deep learning and LLMs are, and how they relate.
📄 [AI Basics Video 1.pdf](<Episode 1/AI Basics Video 1.pdf>)

### Episode 2 — Running Local AI with Ollama ✅
Installing Ollama, `generate()` vs `chat()`, the `system` / `user` / `assistant` roles, and why LLMs are *stateless*.
📄 [Episode 2 notes](<Episode 2/NOTES.md>) · Programs: `first_ai_program.py`, `roles.py`, `chat_bot.py`

---

## Module 2 — Talking to LLMs well

### Episode 3 — Prompt Engineering
**Goal:** get reliable, high-quality answers by writing better prompts.

- What a good prompt contains: role, task, context, format and constraints
- **Zero-shot** vs **few-shot** prompting (giving examples)
- **Chain-of-thought:** asking the model to reason step by step
- Writing strong **system prompts**: persona, rules, tone
- Using delimiters (`"""`, `###`, XML-style tags) to separate instructions from data
- Generation settings: **temperature**, `top_p` and `num_predict` (max tokens), via `options={...}` in Ollama. Episode 5 explains *why* these work
- Prompt templates with Python f-strings
- Common failures: vague prompts, hallucination, prompt injection

**Programs:** `zero_vs_few_shot.py`, `temperature_test.py`, `prompt_templates.py`
**Exercise:** write a prompt that turns any paragraph into a 3-question quiz in the same format every time.

### Episode 4 — Tool Calling (Function Calling)
**Goal:** let the model call your Python functions.

- Why LLMs can't do live math, dates or web lookups on their own
- Describing a tool to the model (name, description, parameters)
- The tool loop: the model asks for a tool → **your code runs it** → you send back a `tool` role message → the model answers
- The new **`tool` role**, which adds to the 3 roles from Episode 2
- Choosing models that support tools well (e.g. `llama3.2`, `qwen3`), and handling bad tool calls from small models

**Programs:** `calculator_tool.py`, `multi_tool_bot.py`
**Exercise:** add a `get_current_time(city)` tool to the chatbot from Episode 2.

### Episode 5 — How LLMs Work: Transformers
**Goal:** understand what happens inside an LLM, in simple words with pictures, without heavy math.

- The big idea: an LLM **predicts the next token**, one token at a time
- **Tokens and tokenization:** why "token" isn't the same as "word", and why Kannada text often uses more tokens than English
- **Embeddings:** each token becomes a list of numbers that captures its meaning
- **Positional encoding:** how the model knows word order
- **Self-attention:** each word "looks at" the other words to understand context (e.g. "bank" in "river bank" vs "bank loan"), with a simple explanation of Query, Key and Value
- **Multi-head attention** and stacking many **layers**
- **Encoder vs decoder:** BERT vs GPT-style models; why chat models are decoder-only
- How a model is trained: **pre-training → instruction tuning → RLHF**, which explains why chat models follow instructions
- Linking back to earlier episodes:
  - **Temperature** is how "random" the pick of the next token is (Episode 3)
  - The **context window** is how many tokens attention can look at, which is why long chats get slow (Episode 2)
  - **Tool calls** are just text the model was trained to produce in a special format (Episode 4)
  - **Parameters** (3B, 8B) and **quantization** (Q4) explain Ollama model sizes
- The paper that started it: *Attention Is All You Need* (2017)

**Programs:** `tokens_demo.py` (see how text splits into tokens), `attention_toy.py` (self-attention on 3 words with NumPy)
**Exercise:** count the tokens in the same sentence written in English and in Kannada, and explain the difference.

---

## Module 3 — LangChain

### Episode 6 — LangChain Basics
**Goal:** learn the framework you'll use for RAG and agents for the rest of the course.

- What LangChain is, why it exists, and when plain Python is enough
- Installing it: `pip install langchain langchain-ollama`
- `ChatOllama`: the same Ollama models, now through LangChain
- Messages (`SystemMessage`, `HumanMessage`, `AIMessage`), which map directly to the roles from Episode 2
- **Prompt templates**: Episode 3's f-string templates, the LangChain way
- Chaining steps together: prompt → model → output parser
- Tools with `@tool` and `.bind_tools()`, the LangChain version of Episode 4
- Streaming responses

**Programs:** `lc_chat.py`, `lc_prompt_templates.py`, `lc_tools.py`
**Exercise:** rebuild the Episode 2 chatbot (with memory) using LangChain, and compare the two versions.

---

## Module 4 — RAG (Retrieval-Augmented Generation)

### Episode 7 — Embeddings & Semantic Search
**Goal:** understand how computers measure "similar meaning".

- **Embeddings** again (from Episode 5), this time for whole sentences and documents
- `ollama.embed()` and LangChain's `OllamaEmbeddings` with an embedding model such as `nomic-embed-text`
- **Cosine similarity**, explained simply
- Keyword search vs semantic search
- **Vector databases:** what they are, with a first look at **ChromaDB** through LangChain's `Chroma` vector store

**Programs:** `first_embedding.py`, `similarity.py`, `semantic_search.py`
**Exercise:** build a search over 20 FAQ sentences that finds the right answer even when the user words the question differently.

### Episode 8 — RAG with LangChain
**Goal:** make the LLM answer questions about *your own* documents.

- Why RAG? The model's knowledge is old and doesn't include your private data
- The RAG pipeline: **load → chunk → embed → store → retrieve → generate**
- A short **under-the-hood** version in ~30 lines of plain Python, so each step is clear
- The same pipeline with LangChain:
  - **Document loaders** for PDFs and text files
  - **Text splitters:** chunk size and overlap
  - **Vector store + retriever**
  - A RAG prompt that tells the model to say "I don't know" when the answer isn't in the documents

**Programs:** `rag_under_the_hood.py`, `lc_rag.py`
**Project:** **Chat with your PDF.** Ask questions about a textbook chapter or a government circular.

### Episode 9 — Better RAG
**Goal:** fix the common reasons RAG gives bad answers.

- Showing **sources / citations** in answers
- Using **metadata** (page number, file name) and filtering on it
- **Hybrid search:** keyword (BM25) + semantic
- **Re-ranking** retrieved chunks
- **Query rewriting:** improving the user's question before searching
- Chatting over documents with memory (combining Episodes 2 and 8)
- Working with Kannada and multilingual text: choosing an embedding model that supports it

**Programs:** `rag_with_citations.py`, `hybrid_search.py`

---

## Module 5 — Agents

### Episode 10 — ReAct Agents from Scratch
**Goal:** understand how an AI agent works by writing one in about 100 lines of Python.

- What an **agent** is: an LLM in a loop that decides which tool to use next
- The **ReAct** pattern: **Thought → Action → Observation**, repeated until the agent reaches a **Final Answer**
- Writing the ReAct loop by hand using tool calling (Episode 4)
- Giving the agent RAG as a tool, so it decides when to search (agentic RAG)
- Safety limits: maximum steps, handling errors, avoiding infinite loops

**Programs:** `react_agent.py`
**Project:** an agent that answers questions using a calculator, a Wikipedia lookup and your document search.

---

## Tools used in this course

| Tool | Used for | From episode |
|------|----------|--------------|
| Python 3.10+ | Everything | 2 |
| Ollama (`llama3.2`, `qwen3`) | Running LLMs locally | 2 |
| NumPy, `tiktoken` | Toy attention and token demos | 5 |
| LangChain (`langchain`, `langchain-ollama`) | Chat, tools and RAG | 6 |
| `nomic-embed-text` | Embeddings | 7 |
| ChromaDB | Vector database | 7 |

> More episodes (agents with LangChain, LangGraph, MCP, evaluation and deployment) will be added after Episode 10. This curriculum may change as the course grows. Libraries like LangChain change quickly, so code in each episode is written against the version current at recording time.
