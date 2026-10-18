import ollama

#1 Role
system_role_content = "You are a wildlife travel writer for a South India travel blog."

#2 Task
user_role_content_v1 = "Write an introduction to Karnataka's wildlife for first-time visitors."

#3 Constraints
user_role_content_v2 = """
Write an introduction to Karnataka's wildlife for first-time visitors.
150 words. Audience: city dwellers who have never been on a safari. Warm, vivid tone. Exactly three parks. No jargon.
"""

#4 Format
user_role_content_v3 = """
rite an introduction to Karnataka's wildlife for first-time visitors.
150 words, city audience, warm and vivid, exactly three parks, no jargon.
Format: three bullets (park, signature animal, best month), then a one-line closing tip.
"""

#5 Examples
user_role_content_v4 = """
Write an introduction to Karnataka's wildlife for first-time visitors.
150 words, city audience, warm and vivid, no jargon. Exactly three parks (Bandipur, Nagarhole, Dandeli), each with one signature animal and the best month. End with one practical tip.
Format: three bullets, then a closing line.
Example bullet: Bandipur: Wild elephants graze at dusk along the forest edge. Best in Nov–Feb.
"""

#Part2: #1 Zero Shot Prompting
user_role_content_v5 = "Write a one-line bullet about Dandeli for a travel blog, with the best month to visit."

#Part2: #2 Few Shots Prompting
user_role_content_v6 = """Write bullets in this style, then do Dandeli.

Bandipur: Wild elephants graze at dusk along the forest edge. Best in Nov–Feb.
Nagarhole: Tigers prowl the tall grass by the Kabini backwaters. Best in Mar–May.
Dandeli:"""

# Think First Prompting
user_role_content_v7 = """
I have 3 days in November, starting from Bengaluru. I want to see elephants and tigers. Think through travel time and season, then recommend parks.
"""


messages = [
    {
        "role": "system",
        "content": system_role_content
    },
    {
        "role": "user",
        "content": user_role_content_v7
    }
]

model_name = "llama3.2:latest"

response = ollama.chat(model = model_name, messages = messages)

print(response.message.content)