# Episode 7 — Notes: Structured Output with Pydantic

These notes cover the theory behind the programs in this folder:

| File | What it shows |
|------|---------------|
| [structured_output.py](structured_output.py) | Extracting a user's name, age and email from a sentence into **one Python object** using `.with_structured_output()` |
| [multilevel_outputs.py](multilevel_outputs.py) | Getting back **a list of objects** by putting one Pydantic model inside another |

Everything runs on the same setup as the earlier episodes: Ollama, `llama3.2` and LangChain's `ChatOllama`. If that isn't working yet, see [Episode 2 notes](<../Episode 2/NOTES.md>) for Ollama, and install LangChain's Ollama package:

```bash
pip install langchain-ollama
```

(`pydantic` is installed along with it.)

---

## 1. Quick Recap from Episodes 5 and 6

- A **Runnable** is any LangChain object with `.invoke()`, `.stream()` and `.batch()`.
- We joined Runnables into chains with `|`, and `StrOutputParser` turned the model's reply into a plain string.
- `RunnableParallel` and `RunnablePassthrough` gave us **dictionaries**, but every value the model wrote was still just text.

So far the model has only given us text for a human to read. This episode is about getting answers that **our code** can use.

---

## 2. The Problem: Text Is Hard for Programs to Use

The commented-out lines at the top of [structured_output.py](structured_output.py) show the problem:

```python
response = llm.invoke(f"Extract user's name, age and email id from the text: {text}")
print(type(response.content))   # <class 'str'>
```

The answer is a **string**. It might be `Name: Varshan, Age: 24`, or a full sentence, or a bulleted list, and the format can change from one run to the next. To get the age out of it, you'd have to search through the text yourself, and that code breaks as soon as the model words its answer differently.

What we really want is this:

```python
response.age   # 24, an actual int
```

| | Plain text | Structured output |
|---|---|---|
| Type you get | `str` | Your own Python class |
| Getting the age | Search through the text | `response.age` |
| Format | Can change on every run | Fixed by you, in advance |
| Good for | A human reading it | Code: databases, APIs, `if` conditions, loops |

> **Analogy:** asking someone to "tell me about yourself" gets you a different story every time. Handing them a form with boxes for **Name**, **Age** and **Email** gets you the same shape every time. Structured output is handing the model a form.

---

## 3. Pydantic: Describing the Form

**Pydantic** is a Python library for describing what your data should look like. You write a class that inherits from `BaseModel`:

```python
from pydantic import BaseModel, Field

class UserDetails(BaseModel):
    name: str = Field(description="Complete Name")
    age: int = Field(description="User's Age")
    email: str = Field(description="User Email")
```

- **`BaseModel`** gives the class its Pydantic powers.
- **`name: str`** is a type hint that says what kind of value the field holds.
- **`Field(description=...)`** explains the field in words. The description is **sent to the model**, so it's really a small prompt for that one field.

### Pydantic checks your data

Here, Pydantic checks and converts the data when an object is created. You can try it without any LLM:

```python
UserDetails(name="Asha", age="24", email="asha@example.com")
# UserDetails(name='Asha', age=24, ...)    "24" was converted to the int 24

UserDetails(name="Asha", age="twenty", email="asha@example.com")
# ValidationError: "twenty" can't be turned into an int

UserDetails(name="Asha", email="asha@example.com")
# ValidationError: age is missing
```

So if something comes out of Pydantic successfully, you know it has every field, with the right types.

---

## 4. `.with_structured_output()` — [structured_output.py](structured_output.py)

One line connects the Pydantic class to the model:

```python
structured_llm = llm.with_structured_output(UserDetails)

response = structured_llm.invoke(f"Extract user's name, age and email id from the text: {text}")
```

`structured_llm` is a new Runnable. The original `llm` isn't changed.

```
          UserDetails (Pydantic class)
                     │
                     ▼
                JSON schema
                     │
prompt ───────────►  ▼
                  llama3.2
                     │
                     ▼
    '{"name": "Varshan", "age": 24, "email": "..."}'   ← text in JSON format
                     │
                     ▼
           Pydantic checks it
                     │
                     ▼
UserDetails(name='Varshan', age=24, email='...')       ← a Python object
```

1. LangChain turns the class into a **JSON schema**, a standard description of the fields and their types. You can see it with `print(UserDetails.model_json_schema())`.
2. The schema is sent to Ollama with your prompt, and the model's reply is held to that format.
3. The reply comes back as JSON text.
4. LangChain parses the JSON and builds a `UserDetails` object.

The model never produces a Python object. It still only writes text; LangChain does the conversion at the end.

### Using the result

`response` is a `UserDetails` object, so you read its fields with a dot:

```python
print(response.name)   # Varshan
print(response.age)    # 24
```

To get a normal dictionary, for example to save as JSON or send to an API, use `.model_dump()`:

```python
dis_output = response.model_dump()
print(dis_output)
# {'name': 'Varshan', 'age': 24, 'email': '...'}
```

| You have | You write | Use it when |
|----------|-----------|-------------|
| A Pydantic object | `response.age` | Working with the data in Python |
| A dictionary | `response.model_dump()["age"]` | Saving it or passing it to something else |

### It works in chains too

`.with_structured_output()` gives you a Runnable, so it fits in a chain like any other step. You don't need `StrOutputParser`, because the output is already parsed:

```python
chain = prompt_template | structured_llm
response = chain.invoke({"text": text})
```

---

## 5. Nested Models and Lists — [multilevel_outputs.py](multilevel_outputs.py)

A `Book` model works well for **one** book:

```python
class Book(BaseModel):
    name: str = Field(description="Book's Name")
    author: str = Field(description="Book's Author")
    publication_year: int = Field(description="The year the book was first published")
```

But the form has room for only one book, so it can't hold an answer to "Suggest 3 well known sci-fi books". The commented-out code in the file shows this single-book version.

The fix is a **second model whose field is a list of the first**:

```python
from typing import List

class BookCollection(BaseModel):
    books: List[Book] = Field(description="a list containing requested books")
```

`List[Book]` means "a list where every item is a `Book`". Pass the **outer** model to `.with_structured_output()`:

```python
structured_llm = llm.with_structured_output(BookCollection)

response = structured_llm.invoke("Suggest 3 well known sci-fi books")
print(response.books)
```

The result has two levels, which is where the file name comes from:

```
BookCollection
└── books (a list)
    ├── Book(name='Dune', author='Frank Herbert', publication_year=1965)
    ├── Book(name='1984', author='George Orwell', publication_year=1949)
    └── Book(name='Do Androids Dream of Electric Sheep?', author='Philip K. Dick', publication_year=1968)
```

`response.books` is a normal Python list, so loops and indexes work as usual:

```python
for book in response.books:
    print(f"{book.name} by {book.author} ({book.publication_year})")

print(response.books[0].author)   # Frank Herbert
```

`.model_dump()` converts every level, so you get a dictionary containing a list of dictionaries:

```python
{"books": [{"name": "Dune", "author": "Frank Herbert", "publication_year": 1965}, ...]}
```

> **Takeaway:** the top level of your output is always one model. To get many items, wrap them: one model that holds a `List` of another model.

---

## 6. Valid Doesn't Mean Correct

Pydantic checks the **shape** of the data, not whether it's **true**. These are real results from `llama3.2` using a model with the same fields as `UserDetails`. Yours may differ, because the model doesn't answer the same way every time.

**The text has no age or email:**

```python
structured_llm.invoke("Extract name, age and email: I'm Asha and I like dosa")
# UserDetails(name='Asha', age=-1, email='-none provided-')
```

We required an `int`, so the model had to give one, and it invented `-1`. Both fields pass validation because `-1` is an int and `-none provided-` is a string.

**The text has everything:**

```python
structured_llm.invoke("Extract name, age and email: I'm Asha, 30, asha@example.com")
# UserDetails(name='Asha', age=30, email='ashea@example.com')
```

The email was **copied wrongly**: `ashea` instead of `asha`. The output is perfectly valid and still wrong, and nothing raised an error.

So in a real project:

- **Allow for missing data.** If a value might not be there, make the field optional, so the model has an honest answer:

  ```python
  from typing import Optional

  age: Optional[int] = Field(default=None, description="User's age, or null if not mentioned")
  ```

- **Check anything that matters.** Before sending an email or saving to a database, check the value in your own code. For example, make sure the extracted email really appears in the original text.

---

## 7. Experiments

**Experiment:** in [structured_output.py](structured_output.py), uncomment the two lines under `# Problem` and run the program a few times. Look at how the text answer changes while the structured one keeps its shape.

**Experiment:** add a `city: str` field to `UserDetails` and change the text so it doesn't mention a city. What does the model put there? Then try the `Optional` version from Section 6.

**Experiment:** change a description to `Field(description="User's name in capital letters")` and see whether the answer changes. This shows that descriptions act like prompts.

**Experiment:** in [multilevel_outputs.py](multilevel_outputs.py), add a `genre: str` field to `Book`. You don't need to change the prompt; the schema is enough.

**Experiment:** ask the same 3-book question using the single `Book` model (the commented-out code). How many books do you get?

**Experiment:** to see the model's reply before it's parsed, use `include_raw=True`:

```python
structured_llm = llm.with_structured_output(UserDetails, include_raw=True)
result = structured_llm.invoke(f"Extract user's name, age and email id from the text: {text}")

print(result["raw"].content)       # the JSON text the model wrote
print(result["parsed"])            # the UserDetails object
print(result["parsing_error"])     # None if parsing worked
```

---

## 8. Running the Programs

```bash
cd "Episode 7"
python3 structured_output.py
python3 multilevel_outputs.py
```

Make sure Ollama is running and the model is downloaded (`ollama pull llama3.2`).

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'langchain_ollama'` | LangChain's Ollama package isn't installed | `pip install langchain-ollama` |
| `AttributeError: 'BookCollection' object has no attribute 'name'` | You're reading a `Book` field from the outer model | Go through the list: `response.books[0].name` |
| `TypeError: 'UserDetails' object is not subscriptable` | You wrote `response["name"]` on a Pydantic object | Use `response.name`, or call `.model_dump()` first |
| A validation error mentioning a field | A value is missing or has the wrong type | Check the field's type and description, or make it `Optional` |
| `ConnectionError` / connection refused | The Ollama server isn't running | Open the Ollama app, or run `ollama serve` |
| `model "llama3.2:latest" not found` | The model isn't downloaded | `ollama pull llama3.2` |

---

## 9. Quick Glossary

| Term | Meaning |
|------|---------|
| **Structured output** | Getting the model's answer in a fixed format that code can use, instead of free text. |
| **Pydantic** | A Python library for describing data as classes, and for checking and converting that data. |
| **`BaseModel`** | The Pydantic class you inherit from to define your own data shape. |
| **`Field(description=...)`** | Adds details to a field. The description is sent to the model along with the schema. |
| **JSON** | A text format for structured data, using keys, values and lists. |
| **JSON schema** | A standard description of what a piece of JSON must look like: its fields and their types. |
| **`.with_structured_output()`** | Returns a new Runnable that makes the model follow a schema and gives you back parsed objects. |
| **`.model_dump()`** | Converts a Pydantic object, including nested ones, into a plain Python dictionary. |
| **Validation** | Checking that data has the right fields and types. It doesn't check that the data is true. |
| **Nested model** | A Pydantic model used as a field inside another model, like `List[Book]` inside `BookCollection`. |
