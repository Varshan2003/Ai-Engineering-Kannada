# Episode 10 — Notes: Document Loaders & Text Splitters

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [document_loader.py](document_loader.py) | Reading a **web page** or a **PDF** into LangChain `Document` objects with `UnstructuredLoader` |
| [text_splitters.py](text_splitters.py) | Cutting those documents into small **chunks** with `RecursiveCharacterTextSplitter` |
| [kaveri-hospital-handbook.pdf](kaveri-hospital-handbook.pdf) | The sample document: an 11-page patient handbook for a made-up hospital |
| [installation.md](installation.md) | The packages this episode needs |

In [Episode 9](<../Episode 9/rag_pipeline.png>) we drew the RAG pipeline. This episode builds its first two steps: **load** and **split**.

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │   LOAD   │ ─► │  SPLIT   │ ─► │  EMBED   │ ─► │  STORE   │ ─► │ RETRIEVE │ ─► LLM
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
  Episode 10      Episode 10      Episode 11      Episode 11      Episode 12
```

---

## 1. Setup

These programs don't call an LLM, so Ollama doesn't need to be running. Install the packages from [installation.md](installation.md) inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate          # your prompt now starts with (.venv)
pip install -U pip
pip install -qU langchain-unstructured unstructured-client "unstructured[pdf]" python-magic
pip install -qU langchain-text-splitters
```

| Package | What it's for |
|---------|---------------|
| `langchain-unstructured` | LangChain's `UnstructuredLoader` |
| `unstructured` + `[pdf]` extra | The library that actually reads the files (PDF, Word, HTML, …) |
| `unstructured-client` | Needed by the loader, also lets you use Unstructured's hosted API |
| `python-magic` | Works out the file type (PDF, HTML, …) from the file itself |
| `langchain-text-splitters` | `RecursiveCharacterTextSplitter` and the other splitters |

> On macOS, `python-magic` needs the `libmagic` library. If you see `failed to find libmagic`, run `brew install libmagic`.

The first run is slow: `unstructured[pdf]` downloads layout-detection models the first time it reads a PDF.

---

## 2. Why We Need Loaders

An LLM only takes **text**. Our knowledge lives in PDFs, web pages, Word files and spreadsheets. Each format stores text differently, and a PDF in particular is a set of instructions for drawing letters at positions on a page, not a neat string.

A **document loader** hides all of that. Whatever the file, you get back the same thing: a list of LangChain `Document` objects.

---

## 3. The `Document` Object

A `Document` has two parts:

```python
Document(
    page_content="Kaveri Demo Hospital",          # the text
    metadata={                                    # facts about the text
        "source": "kaveri-hospital-handbook.pdf",
        "page_number": 1,
        "category": "Title",
        ...
    },
)
```

| Part | Type | What it holds |
|------|------|---------------|
| `page_content` | `str` | The text itself. This is what gets embedded and sent to the LLM. |
| `metadata` | `dict` | Where the text came from: file name, page number, element type … |

Metadata looks unimportant now, but it's what lets a RAG app later say **"according to page 3 of the handbook…"** (Episode 13).

---

## 4. `UnstructuredLoader` — [document_loader.py](document_loader.py)

The same class reads a web page or a local file. You only change the argument:

```python
from langchain_unstructured import UnstructuredLoader

# a web page
loader = UnstructuredLoader(web_url="https://docs.langchain.com/oss/python/integrations/document_loaders/unstructured_file")

# a local file (PDF, .docx, .txt, .html, .pptx, …)
loader = UnstructuredLoader(file_path="kaveri-hospital-handbook.pdf")

docs = loader.load()
print(docs[-1])     # the last Document
```

### One `Document` per *element*, not per page

`UnstructuredLoader` looks at the layout and breaks the file into **elements**: titles, paragraphs, list items, table cells, footers. Each element becomes its own `Document`.

Real numbers for the handbook:

```python
len(docs)                     # 345 Documents from an 11-page PDF
```

| `metadata["category"]` | Count | Example |
|------------------------|-------|---------|
| `Title` | 159 | `'Kaveri Demo Hospital'` |
| `NarrativeText` | 99 | `'Doctor schedules, OPD timings, visiting rules, insurance, billing and patient'` |
| `UncategorizedText` | 58 | `'P A T I E N T H A N D B O O K · 2 0 2 6 E D I T I O N'` |
| `ListItem` | 18 | |
| `Footer` | 11 | |

The longest element is just 103 characters, and the average is 38. So these Documents are already very small.

The metadata on each one includes `source`, `filename`, `filetype`, `page_number`, `category`, `coordinates` (where on the page it was), `languages` and `element_id`.

> **Notice:** `Title` is a guess. Short bold lines in a table, like a doctor's name, also get labelled `Title`. Loaders are good, not perfect, so always print what you got.

### Other loaders you'll see

`UnstructuredLoader` is a general tool. LangChain also has simpler loaders for one format each (in `langchain-community`):

| Loader | Reads | Gives you |
|--------|-------|-----------|
| `TextLoader` | `.txt` | One `Document` for the whole file |
| `PyPDFLoader` | PDF | One `Document` per **page** |
| `WebBaseLoader` | A web page | One `Document` for the page |
| `CSVLoader` | `.csv` | One `Document` per **row** |
| `DirectoryLoader` | A whole folder | Uses another loader on every file |
| `UnstructuredLoader` | Almost anything | One `Document` per **element** |

They all return the same `Document` objects, so everything after this step stays the same whichever one you pick.

### Letting Unstructured group the elements

If 345 tiny pieces is too many, Unstructured can group elements under their headings while loading:

```python
loader = UnstructuredLoader(
    file_path="kaveri-hospital-handbook.pdf",
    chunking_strategy="by_title",
    max_characters=1000,
)
docs = loader.load()
len(docs)     # 17 Documents, category 'CompositeElement'
```

### `.load()` vs `.lazy_load()`

```python
docs = loader.load()             # reads everything, returns a list

for doc in loader.lazy_load():   # yields one Document at a time
    print(doc.metadata["page_number"])
```

Both give the same 345 Documents for the handbook. `.lazy_load()` doesn't keep them all in memory at once, which matters for a 2,000-page PDF or a folder of thousands of files.

---

## 5. Why We Split

Once the text is loaded, why not hand the whole thing to the LLM?

1. **Context window.** Every model has a limit on how much text it can take in one go. A book doesn't fit.
2. **Better search.** In RAG we look for the parts that match the question. A small chunk about "OPD timings" is a clear match. A whole page that mentions OPD timings once, among ten other topics, is a weak one.
3. **Cost and speed.** You pay (in money or time) for every token you send. Sending 3 relevant paragraphs is much cheaper than sending 11 pages.
4. **Less confusion.** Extra, unrelated text gives the model more chances to pick up the wrong fact.

> **Analogy:** a library doesn't hand you every book when you ask a question. It has an index that points you to the right page. Splitting is cutting the book into pages so the index has something to point at.

---

## 6. `RecursiveCharacterTextSplitter` — [text_splitters.py](text_splitters.py)

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=25,
    chunk_overlap=15,
)

chunks = splitter.split_documents(docs)
print(chunks[:5])
```

### The two settings

| Setting | Meaning |
|---------|---------|
| `chunk_size` | The **largest** a chunk may be, in **characters** (not words or tokens) |
| `chunk_overlap` | How many characters at the end of one chunk are **repeated** at the start of the next |

Overlap exists so that a sentence cut at a chunk border still appears whole in at least one chunk.

```
text:     T H A N D B O O K · 2 0 2 6 E D I T I O N
          └──────── chunk 2 ────────┘
                          └──────── chunk 3 ────────┘
                          ◄─ overlap ─►
```

### What "recursive" means

The splitter has a list of places it prefers to cut, from best to worst:

```python
["\n\n", "\n", " ", ""]
#  paragraph   line   word   anywhere
```

It first tries to split on blank lines (paragraphs). Any piece still bigger than `chunk_size` is split again on newlines, then on spaces, and only as a last resort in the middle of a word. It then joins small pieces back together until they're close to `chunk_size`.

So it keeps paragraphs, lines and words whole whenever it can. That's why it's the usual choice.

The simpler **`CharacterTextSplitter`** splits on just one separator (`"\n\n"` by default). If a paragraph is bigger than `chunk_size`, it stays too big and you only get a warning.

### What our settings actually produce

With `chunk_size=25, chunk_overlap=15` on the handbook:

```python
len(chunks)   # 1088 chunks from 345 Documents
```

```
'P A T I E N T H A N D B O'
'T H A N D B O O K · 2 0'
'B O O K · 2 0 2 6 E D I'
'2 0 2 6 E D I T I O N'
'Kaveri Demo Hospital'
'Doctor schedules, OPD'
```

These settings are deliberately extreme so you can **see** the splitting and the overlap. Each chunk repeats more than half of the one before it, and 25 characters is too short to hold a useful fact like "Dr. Vikram Joshi is available Tuesday and Friday, 10 AM to 1 PM". For real RAG, start around:

```python
RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
```

### Choosing sizes

| | Too small | Too big |
|---|---|---|
| What happens | A fact is cut across chunks; chunks have no context | Each chunk covers many topics |
| Effect on search | Matches a phrase, but the answer is in the next chunk | Matches are vague; you send a lot of unrelated text |
| Effect on the LLM | Not enough information to answer | Slower, more expensive, easier to get confused |

A common rule: **overlap ≈ 10–20% of `chunk_size`**. If the overlap is bigger than `chunk_size` you get an error. The default overlap is 200, so always set both values.

### Metadata comes along

`.split_documents()` copies each Document's metadata onto every chunk made from it:

```python
chunks[0].metadata["page_number"]   # 1
chunks[0].metadata["category"]      # 'UncategorizedText'
```

So even a 25-character chunk still knows which file and page it came from. (If you have plain strings instead of Documents, use `.split_text()`, which returns a list of strings with no metadata.)

### A surprise: the splitter never joins Documents

The splitter only cuts **within** each Document. It never glues two Documents together. Our Documents are at most 103 characters long, so:

```python
RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
# still 345 chunks: nothing was big enough to split
```

With `UnstructuredLoader`'s element-by-element output, you have two choices for bigger, more useful chunks:

- Let Unstructured group them: `chunking_strategy="by_title"` (Section 4), **or**
- Join the text yourself and then split:

  ```python
  from langchain_core.documents import Document

  full_text = "\n\n".join(doc.page_content for doc in docs)
  big_doc = Document(page_content=full_text, metadata={"source": "kaveri-hospital-handbook.pdf"})

  chunks = splitter.split_documents([big_doc])   # 31 chunks at chunk_size=500
  ```

  The cost: the per-element metadata, like `page_number`, is lost.

---

## 7. Experiments

**Experiment:** in [document_loader.py](document_loader.py), switch to the commented-out PDF loader. Print `len(docs)` and then `docs[10]`. Which `category` is it?

**Experiment:** print only the narrative paragraphs:

```python
for doc in docs:
    if doc.metadata["category"] == "NarrativeText":
        print(doc.metadata["page_number"], doc.page_content)
```

**Experiment:** in [text_splitters.py](text_splitters.py), set `chunk_overlap=0` and print the first 5 chunks again. Then try `chunk_overlap=30`. What error do you get, and why? What happens if you remove the `chunk_overlap` line completely?

**Experiment:** load the PDF with `chunking_strategy="by_title"`, split with `chunk_size=500, chunk_overlap=50`, and print `len(chunks)` and `chunks[3].page_content`. Can you find the OPD timing for Dr. Vikram Joshi in a single chunk?

**Experiment:** try the loader on a file of your own: a `.docx`, a `.txt`, or your college syllabus PDF.

**Experiment:** compare with a page-based loader:

```bash
pip install langchain-community pypdf
```

```python
from langchain_community.document_loaders import PyPDFLoader

docs = PyPDFLoader("kaveri-hospital-handbook.pdf").load()
print(len(docs))    # how many?
```

---

## 8. Running the Programs

```bash
cd "Episode 10"
python3 document_loader.py
python3 text_splitters.py
```

`document_loader.py` loads the **web page** as written, so it needs an internet connection. The PDF path is relative, so run the programs from inside the `Episode 10` folder.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_unstructured'` | Package not installed, or the venv isn't active | `source .venv/bin/activate`, then the `pip install` from Section 1 |
| `ModuleNotFoundError: No module named 'langchain_text_splitters'` | Package not installed | `pip install langchain-text-splitters` |
| `ImportError: failed to find libmagic` | `python-magic` can't find the system library | macOS: `brew install libmagic` |
| `FileNotFoundError: kaveri-hospital-handbook.pdf` | You ran the program from another folder | `cd "Episode 10"` first |
| `ValueError: Got a larger chunk overlap (…) than chunk size (…)` | `chunk_overlap` is bigger than `chunk_size`. The default overlap is **200**, so setting only a small `chunk_size` causes this too. | Make the overlap smaller, and always set it yourself |
| Very slow first run | Unstructured is downloading its PDF layout models | Wait; later runs are faster |
| `Warning: No languages specified, defaulting to English.` | Just a warning | Ignore it, or pass `languages=["eng"]` |

---

## 9. Quick Glossary

| Term | Meaning |
|------|---------|
| **`Document`** | LangChain's container for text: `page_content` (the text) plus `metadata` (a dict about where it came from). |
| **Document loader** | A class that reads a file, web page or folder and returns a list of `Document`s. |
| **`UnstructuredLoader`** | A loader that reads many file types and splits them into layout **elements**. |
| **Element** | One piece of a page found by Unstructured: a title, paragraph, list item, footer … |
| **`.load()`** | Reads everything and returns a list. |
| **`.lazy_load()`** | Returns Documents one at a time, so large inputs don't fill your memory. |
| **Chunk** | A small piece of a Document, made by a text splitter. Chunks are what get searched in RAG. |
| **Text splitter** | A class that cuts text into chunks of a chosen size. |
| **`chunk_size`** | The largest a chunk may be, in characters. |
| **`chunk_overlap`** | Characters repeated between neighbouring chunks, so facts on a border aren't lost. |
| **`RecursiveCharacterTextSplitter`** | A splitter that tries paragraphs, then lines, then words, then characters, keeping text whole where it can. |
| **`.split_documents()`** | Splits a list of Documents and copies the metadata onto every chunk. |
