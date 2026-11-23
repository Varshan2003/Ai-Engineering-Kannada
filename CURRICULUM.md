# AI Engineering in Kannada — Course Curriculum

A beginner-friendly path from "what is AI?" to building RAG apps and AI agents. Every episode builds on the one before it.

**How this course works**

- **Local first.** Episodes run on your own computer with [Ollama](https://ollama.com), so there's no API key and no cost. From Episode 8 you can also use cloud models (Groq, AWS Bedrock) with the same code.
- **Understand, then build.** After calling models directly from Python, you switch to **LangChain** early and use it for the rest of the course. Key ideas such as RAG, tool calling, the ReAct agent loop and LangGraph are explained from the ground up, so nothing feels like magic.
- **Code with every episode.** Each episode folder has notes (`NOTES.md`) and small, runnable Python programs.
- **Only current LangChain packages.** We use `langchain-core`, the official partner packages (`langchain-ollama`, `langchain-openai`, `langchain-groq`, `langchain-chroma`, `langchain-unstructured`, `langchain-text-splitters`), `langchain` v1 and LangGraph. We **don't** use `langchain-community` (being sunset) or `langchain-classic` (old chains and memory). Where those used to provide a ready-made class, we write the few lines ourselves. When an older tutorial shows a deprecated class, the episode names it and shows what replaced it.

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
| 9 | The RAG Pipeline | A tiny RAG app over a few paragraphs, in plain Python | ✅ Done |
| 10 | Document Loaders & Text Splitters | Loading and chunking text files, PDFs and web pages | ✅ Done |
| 11 | Embeddings & Vector Stores | Search that understands meaning | ✅ Done |
| 12 | RAG with LangChain | "Chat with your PDF" | ✅ Done |
| 13 | Conversational RAG: Chat History & Memory | A PDF chatbot that understands follow-up questions | Next |
| 14 | Advanced RAG | Hybrid search, re-ranking and query rewriting | Planned |
| 15 | Tool Calling | A bot that uses a calculator and a weather tool | Planned |
| 16 | What AI Agents Are: ReAct & the Agent Loop | An agent that thinks, acts and observes | Planned |
| 17 | LangGraph Basics | Your first graph with state, nodes and edges | Planned |
| 18 | LangGraph: Routing, Memory & Human-in-the-Loop | An agent that branches, remembers and asks for approval | Planned |
| 19 | Agentic RAG | An agent that decides when to search your documents | Planned |
| 20 | Multi-Agent Systems | A team of agents that work together | Planned |
| 21 | MCP (Model Context Protocol) | Your own MCP server, used by an agent | Planned |
| 22 | Deploying an AI App | Your RAG/agent app online with FastAPI + Streamlit or AWS | Planned |
| 23 | Capstone Project 1 | A full agent app built from scratch | Planned |
| 24 | Capstone Project 2 / AI Career Roadmap | A second project, or a "what next" finale | Planned |

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
- Generation settings: **temperature**, `top_p` and `num_predict` (max tokens), via `options={...}` in Ollama
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
- **`UnstructuredLoader`** (`langchain-unstructured`): one loader for PDFs, web pages, `.txt`, `.docx` and more
  - It returns one `Document` per **element** (title, paragraph, list item, table cell), each with a `category` and `page_number`
  - The older one-format loaders (`PyPDFLoader`, `WebBaseLoader`, `CSVLoader` …) live in `langchain-community`, which is being sunset, so we don't use them
- `.load()` vs `.lazy_load()` for large files
- Why we split: context window limits, better search, lower cost
- **Text splitters** (`langchain-text-splitters`):
  - `CharacterTextSplitter` vs `RecursiveCharacterTextSplitter`, and why the recursive one is the usual choice
  - `chunk_size` and `chunk_overlap`, and what goes wrong when they're too big or too small
  - `.split_documents()` keeps the metadata on every chunk
- Splitting Kannada text: characters vs words

📄 [Episode 10 notes](<Episode 10/NOTES.md>) · Programs: `document_loader.py`, `text_splitters.py`
**Exercise:** load a PDF, print the number of pages and the metadata of page 1, then split it and compare the number of chunks for different `chunk_size` and `chunk_overlap` values.

### Episode 11 — Embeddings & Vector Stores
**Goal:** do the next two RAG steps, embedding and storing: understand how computers measure "similar meaning", and store your chunks so they can be searched.

- **Embeddings**: turning a sentence or chunk into a list of numbers that captures its meaning
- `ollama.embed()` and LangChain's `OllamaEmbeddings` with an embedding model such as `nomic-embed-text`
- **Cosine similarity**, explained simply
- Keyword search vs semantic search
- **Vector databases:** what they are, with a first look at **ChromaDB** through LangChain's `Chroma` vector store
- Storing the chunks from Episode 10 and searching them with `.similarity_search()`

📄 [Episode 11 notes](<Episode 11/NOTES.md>) · Programs: `vector_embeddings.py`, `vector_store.py`
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

📄 [Episode 12 notes](<Episode 12/NOTES.md>) · Programs: `chatbot.py`
**Project:** **Chat with your PDF.** Ask questions about a textbook chapter or a government circular.

### Episode 13 — Conversational RAG: Chat History & Memory
📄 [Episode 13 notes](<Episode 13/NOTES.md>) · Programs: `conversational_rag.py`

**Goal:** turn the Episode 12 chatbot into one that remembers the conversation, in a simple top-to-bottom script like Episode 12.

- Why the Episode 12 bot fails on follow-ups: "Who is the cardiologist?" → "What are **his** timings?"
- Keeping **chat history** as a list of messages (the same idea as the Episode 2 chatbot)
- `MessagesPlaceholder` in `ChatPromptTemplate` to put the history into the prompt
- **Rewriting the question:** a second chain turns the follow-up into a full question before searching
- Keeping history short with **`trim_messages()`** (by tokens, always starting on a user message)
- Memory that survives a restart: saving the history to a JSON file with `messages_to_dict()` / `messages_from_dict()`
- **Citations:** keeping **page numbers** as metadata, showing them to the model, asking it to cite `[page 3]` after every fact, and reading them back with a regular expression
- Cleaning up the Episode 12 code: building the vector store only once, sending only `page_content` as context, streaming, and `exit` / `history` / `clear` commands
- **What about LangChain's memory classes?** `ConversationBufferMemory`, `create_history_aware_retriever` (`langchain-classic`), `RunnableWithMessageHistory` (deprecated) and the `langchain-community` chat-history stores come up in older tutorials. The modern way is **LangGraph persistence**, in Episode 18

**Exercise:** have a 5-question conversation with the handbook where every question after the first uses "he", "she", "it" or "that".

### Episode 14 — Advanced RAG
**Goal:** fix the common reasons RAG gives bad answers, the things most beginner tutorials skip.

- Debugging RAG: checking **retrieval** first, before blaming the LLM
- Using **metadata** (the page numbers from Episode 13, file name) and filtering on it with Chroma's `filter=`
- **Stricter citations** with structured output (Episode 7): the exact quote + page for every fact, checked by your code (building on Episode 13's `[page 3]` citations)
- **Hybrid search:** keyword search with `rank_bm25` + semantic search with Chroma, merged with **Reciprocal Rank Fusion**, written by hand in ~15 lines (the old `BM25Retriever` / `EnsembleRetriever` are in `langchain-community` / `langchain-classic`)
- **Re-ranking:** retrieving many chunks, then keeping only the best few, with a local **cross-encoder** (`sentence-transformers`) or an LLM that scores each chunk with structured output
- **Query rewriting (multi-query):** an LCEL chain that writes 3 versions of the question, searches with each and removes duplicates (replacing `MultiQueryRetriever`)
- Working with Kannada and multilingual text: choosing an embedding model that supports it

**Programs:** `rag_with_citations.py`, `hybrid_search.py`, `reranking.py`, `multi_query.py`
**Exercise:** find a question the Episode 12 bot gets wrong, and fix it using one of these techniques.

---

## Module 6 — Tools and Agents

### Episode 15 — Tool Calling (Function Calling)
**Goal:** let the model call your Python functions. This is the link between LLMs and agents.

- Why LLMs can't do live math, dates or web lookups on their own
- Describing a tool to the model (name, description, parameters) with `@tool` from `langchain_core.tools`
- Giving tools to the model with `.bind_tools()` and reading `response.tool_calls`
- The tool loop: the model asks for a tool → **your code runs it** → you send back a `ToolMessage` → the model answers
- The new **`tool` role**, which adds to the 3 roles from Episode 2
- Choosing models that support tools well (e.g. `llama3.2`, `qwen3`, or a cloud model from Episode 8), and handling bad tool calls from small models

**Programs:** `01_calculator_tool.py`, `02_multi_tool_bot.py`
**Exercise:** add a `get_current_time(city)` tool to your LangChain chatbot.

### Episode 16 — What AI Agents Are: ReAct & the Agent Loop
**Goal:** understand how an AI agent works by writing one in about 100 lines of Python.

- What an **agent** is: an LLM in a loop that decides which tool to use next
- Chains vs agents: a fixed path vs the model choosing the path
- The **ReAct** pattern: **Thought → Action → Observation**, repeated until the agent reaches a **Final Answer**
- Writing the agent loop by hand using tool calling (Episode 15)
- Safety limits: maximum steps, handling errors, avoiding infinite loops

**Programs:** `react_agent.py`
**Exercise:** give the agent a calculator and a Wikipedia lookup, and ask a question that needs both.

---

## Module 7 — LangGraph

### Episode 17 — LangGraph Basics
**Goal:** learn LangGraph, the industry-standard framework for building agents.

- Why LangGraph: the hand-written loop from Episode 16 gets messy as agents grow
- **State:** the shared data every step can read and update (`TypedDict`, `MessagesState`)
- **Nodes:** plain Python functions that do one job
- **Edges:** connecting nodes, with `START` and `END`
- Building, compiling and running a graph, and drawing it as a picture
- Rebuilding the Episode 16 agent with `ToolNode` and `tools_condition`
- The shortcut: **`create_agent()`** from `langchain` v1, a ready-made agent graph built on LangGraph (it replaces the older `create_react_agent` and `AgentExecutor`)

**Programs:** `01_first_graph.py`, `02_langgraph_agent.py`, `03_create_agent.py`

### Episode 18 — LangGraph: Routing, Memory & Human-in-the-Loop
**Goal:** build agents that make decisions, retry, remember conversations, and stop to ask a human.

- **Conditional edges:** choosing the next node based on the state
- **Loops:** going back to an earlier node until a check passes, with a step limit
- **Memory, the official way (LangGraph persistence):**
  - **Short-term memory:** a checkpointer (`InMemorySaver`, or `SqliteSaver` from `langgraph-checkpoint-sqlite` to survive restarts) that saves the conversation per `thread_id`
  - Several users or chats at once: one `thread_id` each
  - Keeping long chats small: trimming or summarising old messages inside the graph
  - **Long-term memory:** a `Store` for facts that last across threads ("my name is Ravi", "I prefer answers in Kannada")
  - Rebuilding the Episode 13 hospital chatbot with a checkpointer instead of `chat_history.json`
- **Human-in-the-loop:** pausing with `interrupt()` for approval before an important action, then resuming (this also needs a checkpointer)
- Streaming each step of the graph to see what the agent is doing

**Programs:** `01_routing.py`, `02_loops.py`, `03_memory.py`, `04_human_in_the_loop.py`
**Exercise:** an agent that drafts an email and waits for your "yes" before "sending" it.

### Episode 19 — Agentic RAG
**Goal:** tie the RAG section to agents: an agent that decides *when* and *how* to search.

- Plain RAG vs agentic RAG: always searching vs searching only when needed
- Giving the agent the Episode 12–14 retriever as a **tool**
- **Grading** retrieved chunks and **rewriting the question** when they aren't relevant
- Choosing between several sources: the hospital handbook, the web, or no search at all

**Programs:** `agentic_rag.py`
**Project:** a hospital assistant that answers from the handbook, and says so when it needs another source.

### Episode 20 — Multi-Agent Systems
**Goal:** split a big job between several specialised agents.

- When one agent isn't enough: too many tools, too many instructions
- The **supervisor** pattern: one agent hands work to the others
- **Handoffs** between agents, and sharing state between them
- Common patterns: researcher + writer, planner + workers
- The costs: more LLM calls, more tokens, harder debugging

**Programs:** `supervisor_agents.py`
**Project:** a research team: one agent searches, one writes, one reviews.

---

## Module 8 — MCP and Deployment

### Episode 21 — MCP (Model Context Protocol)
**Goal:** connect agents to tools and data in a standard way.

- What MCP is and why it exists: one standard instead of a custom integration for every tool
- **Servers, clients and hosts**; tools, resources and prompts
- Writing your own MCP server in Python
- Using MCP servers from a LangChain / LangGraph agent with `langchain-mcp-adapters`
- Using MCP servers in apps like Claude Desktop and VS Code
- Security: only connecting servers you trust

**Programs:** `mcp_server.py`, `mcp_agent.py`

### Episode 22 — Deploying an AI App
**Goal:** put your app online so others can use it.

- Turning a chain or agent into an API with **FastAPI**
- A simple chat UI with **Streamlit**
- Streaming answers to the UI
- Keeping secrets safe in production (no keys in code)
- Deploying on **AWS**, building on the Bedrock setup from Episode 8
- Watching costs and setting limits

**Programs:** `api.py`, `app.py`
**Project:** the hospital RAG chatbot, live on the internet.

---

## Module 9 — Capstone

### Episode 23 — Capstone Project 1: A Full Agent App from Scratch
**Goal:** use everything from the course in one real project.

- Planning the app: what it does, which tools and data it needs
- Building it step by step: RAG, tools, a LangGraph agent, memory and a UI
- Testing it with real questions and fixing what breaks
- Deploying it (Episode 22)

### Episode 24 — Capstone Project 2, or AI Career Roadmap & What Next
**Goal:** finish the course properly.

- Either a second capstone project, or:
- An **AI engineer career roadmap**: what to learn next, building a portfolio, and the projects worth showing
- A recap of the whole course, and where to go from here

---

## Tools used in this course

| Tool | Used for | From episode |
|------|----------|--------------|
| Python 3.10+ | Everything | 2 |
| Ollama (`llama3.2`, `qwen3`) | Running LLMs locally | 2 |
| LangChain (`langchain-core`, `langchain-ollama`) | Chat, prompts, chains, messages, tools | 4 |
| Pydantic | Structured output | 7 |
| `python-dotenv` | Loading API keys from `.env` | 8 |
| Groq (`langchain-groq`) | Fast cloud models with a free tier | 8 |
| AWS Bedrock (`langchain-openai` + Bedrock Mantle) | Cloud models from many providers | 8 |
| `langchain-unstructured`, `unstructured[pdf]` | Document loaders | 10 |
| `langchain-text-splitters` | Chunking documents | 10 |
| `embeddinggemma-2` (via Ollama) | Embeddings | 11 |
| ChromaDB (`langchain-chroma`) | Vector database | 11 |
| `rank_bm25` | Keyword search for hybrid RAG | 14 |
| `sentence-transformers` | Local cross-encoder for re-ranking | 14 |
| LangGraph (`langgraph`), `langchain` v1 (`create_agent`) | Agents as graphs | 17 |
| `langgraph-checkpoint-sqlite` | Saving agent memory to disk | 18 |
| MCP (`mcp`, `langchain-mcp-adapters`) | Connecting agents to tools | 21 |
| FastAPI, Streamlit | Serving and UI for deployed apps | 22 |

**Not used in this course:** `langchain-community` (being sunset; integrations are moving to partner packages) and `langchain-classic` (legacy chains, retrievers and memory such as `ConversationBufferMemory`, `EnsembleRetriever`, `MultiQueryRetriever`, `create_history_aware_retriever`). `RunnableWithMessageHistory` is also deprecated in favour of LangGraph persistence.

> This curriculum may change as the course grows. Libraries like LangChain change quickly, so code in each episode is written against the version current at recording time.
