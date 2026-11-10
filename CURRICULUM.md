# AI Engineering in Kannada — Course Curriculum

A beginner-friendly path from "what is AI?" to building RAG apps and AI agents. Every episode builds on the one before it.

**How this course works**

- **Local first.** Episodes run on your own computer with [Ollama](https://ollama.com), so there's no API key and no cost. From Episode 8 you can also use cloud models (Groq, AWS Bedrock) with the same code.
- **Understand, then build.** After calling models directly from Python, you switch to **LangChain** early and use it for the rest of the course. Key ideas such as RAG, tool calling, how Transformers work and the ReAct agent loop are explained from the ground up, so nothing feels like magic.
- **Code with every episode.** Each episode folder has notes (`NOTES.md`) and small, runnable Python programs.

**What you need:** a laptop with 8 GB+ RAM, Python 3.10 or newer, and Ollama installed (setup is in [Episode 2](<Episode 2/NOTES.md>)). For Episode 8, a free Groq account and, optionally, an AWS account.

---

## Course map

| # | Episode | You will build | Status |
|---|---------|----------------|--------|
| 1 | AI Basics | — | ✅ Done |
| 2 | Running Local AI with Ollama | A chatbot with memory | ✅ Done |
| 3 | Prompt Engineering | A prompt playground | ✅ Done |
| 4 | LangChain Basics | Your first LangChain programs with `ChatOllama` | ✅ Done |
| 5 | Prompt Templates, Runnables & Chains | A reusable "teacher" chain with streaming | ✅ Done |
| 6 | Sequence, Parallel & Passthrough | Chains that branch out and pass data along | ✅ Done |
| 7 | Structured Output with Pydantic | Extracting data into Python objects and lists | ✅ Done |
| 8 | Using Cloud LLMs: Groq & AWS Bedrock | The same LangChain code on cloud models | ✅ Done |
| 9 | The RAG Pipeline | A tiny RAG app over a few paragraphs, in plain Python | Next |
| 10 | Document Loaders & Text Splitters | Loading and chunking text files, PDFs and web pages | Planned |
| 11 | Embeddings & Vector Stores | Search that understands meaning | Planned |
| 12 | RAG with LangChain | "Chat with your PDF" | Planned |
| 13 | Better RAG | A RAG app with citations and better retrieval | Planned |
| 14 | Tool Calling | A bot that uses a calculator and a weather tool | Planned |
| 15 | How LLMs Work: Transformers | A toy attention calculation | Planned |
| 16 | ReAct Agents from Scratch | An agent that thinks, acts and observes | Planned |

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

### Episode 3 — Prompt Engineering ✅
📄 [Episode 3 notes](<Episode 3/NOTES.md>) · Programs: `prompts.py`

**Goal:** get reliable, high-quality answers by writing better prompts.

- What a good prompt contains: role, task, context, format and constraints
- **Zero-shot** vs **few-shot** prompting (giving examples)
- **Chain-of-thought:** asking the model to reason step by step
- Writing strong **system prompts**: persona, rules, tone
- Using delimiters (`"""`, `###`, XML-style tags) to separate instructions from data
- Generation settings: **temperature**, `top_p` and `num_predict` (max tokens), via `options={...}` in Ollama. Episode 15 explains *why* these work
- Prompt templates with Python f-strings
- Common failures: vague prompts, hallucination, prompt injection

**Exercise:** write a prompt that turns any paragraph into a 3-question quiz in the same format every time.

---

## Module 3 — LangChain

### Episode 4 — LangChain Basics ✅
📂 [Episode 4 folder](<Episode 4/>) · Programs: `01_langchain_intro.py`, `02_langchain_roles.py`, `03_temperature.py`

**Goal:** learn the framework you'll use for RAG and agents for the rest of the course.

- What LangChain is, why it exists, and when plain Python is enough
- Installing it: `pip install langchain-ollama`
- `ChatOllama`: the same Ollama models, now through LangChain, with `.invoke()`
- Messages (`SystemMessage`, `HumanMessage`, `AIMessage`, or `(role, text)` tuples), which map directly to the roles from Episode 2
- **Temperature** in LangChain: the same question at `0`, `0.5` and `2`

### Episode 5 — Prompt Templates, Runnables & Chains ✅
📄 [Episode 5 notes](<Episode 5/NOTES.md>) · Programs: `01_prompt_templates.py`, `02_runnables.py`, `03_sequences.py`

**Goal:** turn one-off prompts into reusable building blocks and join them together.

- **`ChatPromptTemplate`**: Episode 3's f-string templates, the LangChain way, with `{placeholders}`
- **Runnables**: one shared interface, `.invoke()`, `.stream()` and `.batch()`
- **`StrOutputParser`**: getting plain text out of an `AIMessage`
- Chaining steps with `|` (**LCEL**): prompt → model → output parser
- **Streaming** responses token by token

### Episode 6 — Sequence, Parallel & Passthrough ✅
📄 [Episode 6 notes](<Episode 6/NOTES.md>) · Programs: `01_runnable_sequence.py`, `02_runnable_paralle.py`, `03_runnable_passthrough.py`

**Goal:** build chains that are more than a straight line.

- **`RunnableSequence`**: what `|` really builds
- **`RunnableParallel`**: running several chains on the same input and getting back a dictionary
- **`RunnablePassthrough`** and **`.assign()`**: feeding one chain's answer into the next while keeping the original input
- `.assign()` vs `RunnableParallel`, and the plain-dictionary shortcut used in RAG code later

**Exercise:** rebuild the Episode 2 chatbot (with memory) using LangChain, and compare the two versions.

### Episode 7 — Structured Output with Pydantic ✅
📄 [Episode 7 notes](<Episode 7/NOTES.md>) · Programs: `structured_output.py`, `multilevel_outputs.py`

**Goal:** get answers your code can use, not just text for a human to read.

- Why plain text is hard for programs to use
- **Pydantic** models: `BaseModel`, type hints and `Field(description=...)`
- **`.with_structured_output()`**: Pydantic class → JSON schema → Python object
- `.model_dump()` to get a plain dictionary
- **Nested models and lists**: `List[Book]` inside `BookCollection`
- Valid doesn't mean correct: `Optional` fields and checking important values

---

## Module 4 — Cloud LLMs

### Episode 8 — Using Cloud LLMs: Groq & AWS Bedrock ✅
📄 [Episode 8 notes](<Episode 8/NOTES.md>) · [AWS Bedrock notes](<Episode 8/AWS_BEDROCK_NOTES.md>) · Programs: `groq_chat.py`, `aws_chat.py`

**Goal:** move from the small model on your laptop to powerful cloud models, using the same LangChain code.

- Local vs cloud LLMs: model size, speed, cost and privacy
- **API keys**: what they are, keeping them in a `.env` file with `python-dotenv`, and out of Git with `.gitignore`
- **Groq**: a free API key and fast open models with `ChatGroq`; free-tier rate limits
- **AWS Bedrock**: many companies' models with one AWS account; budget alerts; Bedrock API keys
- Why we don't start with `langchain-aws`: IAM, boto3 and `aws configure` vs one API key
- **Bedrock Mantle**, Bedrock's OpenAI-compatible endpoint, used through `ChatOpenAI` with `base_url`
- Switching between Ollama, Groq and Bedrock by changing **one line**

**Exercise:** run Episode 7's structured output program on a cloud model and compare it with `llama3.2`.

---

## Module 5 — RAG (Retrieval-Augmented Generation)

### Episode 9 — The RAG Pipeline
**Goal:** understand what RAG is, why we need it, and how its steps fit together, before using LangChain's RAG tools.

- Why RAG? The model's knowledge stops at its training date and doesn't include your private data, so it guesses (hallucinates)
- Three ways to give a model new knowledge: pasting the whole document into the prompt (and why the context window limits it), **RAG**, and fine-tuning
- The RAG pipeline: **load → split → embed → store → retrieve → generate**
  - **Indexing** (done once): load → split → embed → store
  - **Answering** (done for every question): retrieve → generate
- What each step does, with a simple picture. Episodes 10–12 cover each step in detail
- A tiny RAG in plain Python: a few paragraphs, simple keyword matching to pick the relevant ones, and a `ChatPromptTemplate` that answers only from them
- A RAG prompt that tells the model to say "I don't know" when the answer isn't in the context
- Where RAG is used: company chatbots, "chat with your PDF", customer support, searching notes

**Programs:** `01_why_rag.py` (the model guessing without context), `02_tiny_rag.py`
**Exercise:** ask the tiny RAG a question whose answer isn't in the paragraphs. Does it say "I don't know"?

### Episode 10 — Document Loaders & Text Splitters
**Goal:** do the first two RAG steps, loading and splitting, on your own documents.

- LangChain's **`Document`**: `page_content` (the text) + `metadata` (source file, page number …)
- **Document loaders** (`langchain-community`):
  - `TextLoader` for `.txt` files
  - `PyPDFLoader` for PDFs: one `Document` per page
  - `WebBaseLoader` for web pages
  - `CSVLoader` for spreadsheets: one `Document` per row
  - `DirectoryLoader` for a whole folder of files
- `.load()` vs `.lazy_load()` for large files
- Why we split: context window limits, better search, lower cost
- **Text splitters** (`langchain-text-splitters`):
  - `CharacterTextSplitter` vs `RecursiveCharacterTextSplitter`, and why the recursive one is the usual choice
  - `chunk_size` and `chunk_overlap`, and what goes wrong when they're too big or too small
  - `.split_documents()` keeps the metadata on every chunk
- Splitting Kannada text: characters vs words

**Programs:** `01_text_loader.py`, `02_pdf_loader.py`, `03_web_loader.py`, `04_text_splitter.py`
**Exercise:** load a PDF, print the number of pages and the metadata of page 1, then split it and compare the number of chunks for different `chunk_size` and `chunk_overlap` values.

### Episode 11 — Embeddings & Vector Stores
**Goal:** do the next two RAG steps, embedding and storing: understand how computers measure "similar meaning", and store your chunks so they can be searched.

- **Embeddings**: turning a sentence or chunk into a list of numbers that captures its meaning
- `ollama.embed()` and LangChain's `OllamaEmbeddings` with an embedding model such as `nomic-embed-text`
- **Cosine similarity**, explained simply
- Keyword search vs semantic search
- **Vector databases:** what they are, with a first look at **ChromaDB** through LangChain's `Chroma` vector store
- Storing the chunks from Episode 10 and searching them with `.similarity_search()`

**Programs:** `first_embedding.py`, `similarity.py`, `semantic_search.py`
**Exercise:** build a search over 20 FAQ sentences that finds the right answer even when the user words the question differently.

### Episode 12 — RAG with LangChain
**Goal:** make the LLM answer questions about *your own* documents.

- A short **under-the-hood** version in ~30 lines of plain Python, so each step is clear
- The same pipeline with LangChain:
  - Loaders and splitters (Episode 10) → embeddings and vector store (Episode 11)
  - Turning the vector store into a **retriever**
  - A RAG chain built with `RunnableParallel` and `RunnablePassthrough` (Episode 6)
  - A RAG prompt that tells the model to say "I don't know" when the answer isn't in the documents
- Running the same RAG chain on Ollama or on a cloud model (Episode 8)

**Programs:** `rag_under_the_hood.py`, `lc_rag.py`
**Project:** **Chat with your PDF.** Ask questions about a textbook chapter or a government circular.

### Episode 13 — Better RAG
**Goal:** fix the common reasons RAG gives bad answers.

- Showing **sources / citations** in answers, using structured output (Episode 7)
- Using **metadata** (page number, file name) and filtering on it
- **Hybrid search:** keyword (BM25) + semantic
- **Re-ranking** retrieved chunks
- **Query rewriting:** improving the user's question before searching
- Chatting over documents with memory (combining Episodes 2 and 12)
- Working with Kannada and multilingual text: choosing an embedding model that supports it

**Programs:** `rag_with_citations.py`, `hybrid_search.py`

---

## Module 6 — Tools and what's inside an LLM

### Episode 14 — Tool Calling (Function Calling)
**Goal:** let the model call your Python functions.

- Why LLMs can't do live math, dates or web lookups on their own
- Describing a tool to the model (name, description, parameters) with LangChain's `@tool`
- Giving tools to the model with `.bind_tools()` and reading `response.tool_calls`
- The tool loop: the model asks for a tool → **your code runs it** → you send back a `ToolMessage` → the model answers
- The new **`tool` role**, which adds to the 3 roles from Episode 2
- Choosing models that support tools well (e.g. `llama3.2`, `qwen3`, or a cloud model from Episode 8), and handling bad tool calls from small models

**Programs:** `01_calculator_tool.py`, `02_multi_tool_bot.py`
**Exercise:** add a `get_current_time(city)` tool to your LangChain chatbot.

### Episode 15 — How LLMs Work: Transformers
**Goal:** understand what happens inside an LLM, in simple words with pictures, without heavy math.

- The big idea: an LLM **predicts the next token**, one token at a time
- **Tokens and tokenization:** why "token" isn't the same as "word", and why Kannada text often uses more tokens than English
- **Token embeddings:** each token becomes a list of numbers that captures its meaning (like the sentence embeddings in Episode 11)
- **Positional encoding:** how the model knows word order
- **Self-attention:** each word "looks at" the other words to understand context (e.g. "bank" in "river bank" vs "bank loan"), with a simple explanation of Query, Key and Value
- **Multi-head attention** and stacking many **layers**
- **Encoder vs decoder:** BERT vs GPT-style models; why chat models are decoder-only
- How a model is trained: **pre-training → instruction tuning → RLHF**, which explains why chat models follow instructions
- Linking back to earlier episodes:
  - **Temperature** is how "random" the pick of the next token is (Episodes 3 and 4)
  - The **context window** is how many tokens attention can look at, which is why long chats get slow (Episode 2) and why RAG sends only a few chunks (Episode 9)
  - **Structured output** and **tool calls** are just text the model was trained to produce in a special format (Episodes 7 and 14)
  - **Parameters** (3B and 8B vs hundreds of billions) and **quantization** (Q4) explain Ollama model sizes, and why cloud models are stronger (Episode 8)
  - Cloud providers charge **per token** (Episode 8)
- The paper that started it: *Attention Is All You Need* (2017)

**Programs:** `tokens_demo.py` (see how text splits into tokens), `attention_toy.py` (self-attention on 3 words with NumPy)
**Exercise:** count the tokens in the same sentence written in English and in Kannada, and explain the difference.

---

## Module 7 — Agents

### Episode 16 — ReAct Agents from Scratch
**Goal:** understand how an AI agent works by writing one in about 100 lines of Python.

- What an **agent** is: an LLM in a loop that decides which tool to use next
- The **ReAct** pattern: **Thought → Action → Observation**, repeated until the agent reaches a **Final Answer**
- Writing the ReAct loop by hand using tool calling (Episode 14)
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
| LangChain (`langchain`, `langchain-ollama`) | Chat, chains, tools and RAG | 4 |
| Pydantic | Structured output | 7 |
| `python-dotenv` | Loading API keys from `.env` | 8 |
| Groq (`langchain-groq`) | Fast cloud models with a free tier | 8 |
| AWS Bedrock (`langchain-openai` + Bedrock Mantle) | Cloud models from many providers | 8 |
| `langchain-community`, `pypdf` | Document loaders | 10 |
| `langchain-text-splitters` | Chunking documents | 10 |
| `nomic-embed-text` | Embeddings | 11 |
| ChromaDB | Vector database | 11 |
| NumPy, `tiktoken` | Toy attention and token demos | 15 |

> More episodes (agents with LangChain, LangGraph, MCP, evaluation and deployment) will be added after Episode 16. This curriculum may change as the course grows. Libraries like LangChain change quickly, so code in each episode is written against the version current at recording time.
