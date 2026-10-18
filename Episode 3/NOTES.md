# Episode 3 — Notes: Prompt Engineering

These notes cover the theory behind the program in this folder:

| File | What it shows |
|------|---------------|
| [prompts.py](prompts.py) | One task improved step by step (role → task → constraints → format → examples), then zero-shot, few-shot and think-first prompting |

Everything runs on the same setup as Episode 2: Ollama, `llama3.2` and `ollama.chat()`. If that isn't working yet, see [Episode 2 notes](<../Episode 2/NOTES.md>).

---

## 1. What is Prompt Engineering?

A **prompt** is the text you send to the model. **Prompt engineering** is the skill of writing that text so the model gives you the answer you actually want: the right content, length, tone and format, every time.

- The model only knows what you tell it. A vague prompt gets a vague (or random) answer.
- You don't change the model or its code. You only change the **words** you send.
- Better prompts mean fewer retries, more predictable output, and output your Python code can rely on.

> **Analogy:** asking a new employee to "write something about wildlife" vs giving them a clear brief: who it's for, how long, which parks, and a sample of what you want. Same employee, very different result.

---

## 2. The Five Building Blocks of a Good Prompt

[prompts.py](prompts.py) takes **one task**, *"introduce Karnataka's wildlife to first-time visitors"*, and improves the prompt one block at a time. Each version keeps everything from the previous one and adds something new.

| # | Block | Question it answers | Where it goes |
|---|-------|---------------------|---------------|
| 1 | **Role** | *Who* should the model be? | `system` message |
| 2 | **Task** | *What* should it do? | `user` message |
| 3 | **Constraints** | *How long, for whom, what tone, what to avoid?* | `user` message |
| 4 | **Format** | *What shape* should the answer have? | `user` message |
| 5 | **Examples** | *What does a good answer look like?* | `user` message |

### 1. Role — `system_role_content`

```python
system_role_content = "You are a wildlife travel writer for a South India travel blog."
```

- Goes in the **`system`** message (from Episode 2), so it applies to every answer.
- Sets the **voice and expertise**. A "travel writer" writes vivid, reader-friendly text; a "wildlife biologist" would write something more technical.

### 2. Task — `user_role_content_v1`

```python
"Write an introduction to Karnataka's wildlife for first-time visitors."
```

- A clear action verb (**Write**, **Summarise**, **List**, **Explain**) and a clear subject.
- On its own this works, but the model has to **guess** everything else: length, tone, how many parks, whether to use bullets. Run it twice and you'll get two quite different answers.

### 3. Constraints — `user_role_content_v2`

```
150 words. Audience: city dwellers who have never been on a safari. Warm, vivid tone. Exactly three parks. No jargon.
```

Constraints remove the guessing:

| Constraint | Controls |
|------------|----------|
| `150 words` | Length |
| `Audience: city dwellers who have never been on a safari` | Who it's written for, and so the difficulty level |
| `Warm, vivid tone` | Style |
| `Exactly three parks` | Scope (be specific: "exactly three", not "a few") |
| `No jargon` | What to **avoid** |

### 4. Format — `user_role_content_v3`

```
Format: three bullets (park, signature animal, best month), then a one-line closing tip.
```

- Tells the model the **shape** of the answer, not just the content.
- Very important when your **code** will use the output later. A fixed format can be split, parsed or shown in a UI reliably.
- Common formats: bullets, numbered steps, a table, JSON, "one line only", "answer Yes or No".

### 5. Examples — `user_role_content_v4`

```
Exactly three parks (Bandipur, Nagarhole, Dandeli), each with one signature animal and the best month.
...
Example bullet: Bandipur: Wild elephants graze at dusk along the forest edge. Best in Nov–Feb.
```

- Showing **one sample** of the output is often clearer than a paragraph of instructions.
- The model copies the example's **length, structure and style**.
- This version also adds **context** (the three park names), so the model doesn't pick parks on its own.

### How the prompt grows

```
v1:  Task
v2:  Task + Constraints
v3:  Task + Constraints + Format
v4:  Task + Constraints + Format + Examples
     (Role stays in the system message the whole time)
```

**Experiment:** run v1 and v4 three times each. v1 changes a lot between runs; v4 looks almost the same every time. That consistency is the goal.

---

## 3. Zero-Shot vs Few-Shot Prompting

A **"shot"** is one **example** included in the prompt.

### Zero-shot — `user_role_content_v5`

```python
"Write a one-line bullet about Dandeli for a travel blog, with the best month to visit."
```

- **No examples.** The model relies only on the instruction.
- Quick to write, and fine for simple or common tasks.
- The style is up to the model, so results vary.

### Few-shot — `user_role_content_v6`

```
Write bullets in this style, then do Dandeli.

Bandipur: Wild elephants graze at dusk along the forest edge. Best in Nov–Feb.
Nagarhole: Tigers prowl the tall grass by the Kabini backwaters. Best in Mar–May.
Dandeli:
```

- **Two examples** (two shots), then the model completes the pattern.
- The prompt **ends with `Dandeli:`**, an unfinished line, so the most natural next thing for the model to write is a bullet in exactly the same style.
- The model picks up the pattern on its own: `Park: <vivid sentence with an animal>. Best in <months>.`

### When to use which

| | Zero-shot | Few-shot |
|---|---|---|
| Examples in prompt | 0 | 1 – 5 (one example = "one-shot") |
| Prompt length | Short | Longer (uses more tokens) |
| Output consistency | Varies | Matches the examples closely |
| Best for | Simple, well-known tasks | A specific style or format, or tricky tasks |

**Tips for few-shot:**
- Keep examples **consistent** with each other. The model copies mistakes too.
- Use examples that are **different** enough (different parks, animals and months) so the model learns the pattern, not one specific answer.
- 2–3 good examples are usually enough.

---

## 4. Think-First Prompting (Chain-of-Thought) — `user_role_content_v7`

```
I have 3 days in November, starting from Bengaluru. I want to see elephants and tigers.
Think through travel time and season, then recommend parks.
```

- Some questions need **reasoning**, not just facts: travel time, the season, what fits into 3 days.
- **"Think through … then recommend"** asks the model to **work it out step by step first**, and only then give the answer.
- This is called **Chain-of-Thought (CoT)** prompting.

### Why it helps

An LLM writes **one token at a time** (more on this in Episode 5). If it has to give the final answer immediately, it has no "space" to reason. When it writes the steps out first, each step becomes part of the text it reads while writing the next one, so the final answer is built on that reasoning.

```
Without CoT:  question ──► answer                     (jumps to a conclusion)
With CoT:     question ──► step 1 ──► step 2 ──► answer   (reasons first)
```

### Common phrasings

- "Think step by step."
- "First list the factors, then decide."
- "Explain your reasoning, then give the final answer on the last line."

**Things to know:**
- Answers become **longer and slower**, so only use it when the task needs reasoning.
- Small models like `llama3.2` (3B) can still make mistakes in their reasoning. Always check facts such as distances and seasons.
- If your code needs only the result, ask for it in a fixed place, e.g. *"End with: `Final answer: <parks>`"*.

---

## 5. Running the Program

Only one prompt is sent at a time. Choose which one by changing the `user` message's `content` in [prompts.py](prompts.py):

```python
messages = [
    {"role": "system", "content": system_role_content},
    {"role": "user",   "content": user_role_content_v7}   # ← change v7 to v1, v2, ... v6
]
```

Then run:

```bash
cd "Episode 3"
python3 prompts.py
```

**Experiment:** go through `v1` → `v7` in order and compare the answers side by side.

### Triple quotes (`"""`)

Most prompts in the file use Python's triple-quoted strings:

```python
user_role_content_v2 = """
Write an introduction ...
150 words. ...
"""
```

- They let a prompt span **several lines**, which keeps long prompts readable.
- The line breaks are sent to the model too. That's fine; it helps separate the task, constraints and format.

---

## 6. Prompt Checklist

Before sending a prompt, check:

- [ ] **Role:** did I tell the model who to be? (system message)
- [ ] **Task:** is there one clear action verb?
- [ ] **Context:** did I give the facts it needs (names, data, the audience)?
- [ ] **Constraints:** length, tone, scope, what to avoid?
- [ ] **Format:** bullets, table, JSON, one line?
- [ ] **Examples:** would one or two samples make it clearer?
- [ ] **Reasoning:** does the task need "think step by step"?

### Common mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Too vague | "Tell me about wildlife." | Add a task, audience and length |
| Fuzzy numbers | "A few parks", "short" | "Exactly three parks", "150 words" |
| Mixed instructions | Asking for bullets *and* "one paragraph" | Make the format rule clear and single |
| Trusting facts blindly | Using the model's best months or travel times as-is | Small models can **hallucinate**. Verify important facts |

---

## 7. Quick Glossary

| Term | Meaning |
|------|---------|
| **Prompt** | The text/instruction you send to the model. |
| **Prompt engineering** | Writing and improving prompts to get reliable, high-quality answers. |
| **Role / persona** | Who the model should act as, usually set in the `system` message. |
| **Constraint** | A rule that limits the answer: length, tone, audience, scope, what to avoid. |
| **Format** | The required shape of the output: bullets, table, JSON, etc. |
| **Shot** | One example included in the prompt. |
| **Zero-shot** | Prompting with instructions only, no examples. |
| **Few-shot** | Prompting with a few examples so the model copies the pattern. |
| **Chain-of-Thought (CoT)** | Asking the model to reason step by step before answering. |
| **Hallucination** | When the model confidently states something that is false. |
