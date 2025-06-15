# main.py
from datetime import datetime
from memory_store import MemoryStore
from embedding_utils import embed_text
import requests
import ollama
# Tools
from tools import call_tool_from_input
# Auto tagging
from tag_extractor import extract_tags_from_query
# import Prompt library
from prompt import ASSISSTANT_PROMPT, USER_PROMPT
from config import MODEL_NAME
# import utlities
from utilities import *


OLLAMA_CHAT_URL = "http://localhost:11434"
OLLAMA_MODEL = MODEL_NAME

store = MemoryStore()
LAST_CHAT = []

# ✅ System prompt loaded only once
SYSTEM_PROMPT = ASSISSTANT_PROMPT

print("🤖 Memory Bot Started. Use '!save', '!remember', '!recall', or ask anything.")

def chat_with_model_stream(symbol: str, prompt: str, model=MODEL_NAME):
    if (len(LAST_CHAT) > 0):
        messages = [SYSTEM_PROMPT, USER_PROMPT[0], LAST_CHAT[0][0], {"role": "user", "content": prompt}]
    else:
        messages = [SYSTEM_PROMPT, USER_PROMPT[0], {"role": "user", "content": prompt}]

    response_stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True  # Enable streaming
    )

    # Stream the response chunks
    full_response = f"{symbol}: "  # Add emoji prefix
    print(full_response, end='', flush=True)

    for chunk in response_stream:
        token = chunk.get('message', {}).get('content', '')
        print(token, end='', flush=True)
        full_response += token

    return full_response

## A function to save the reply into a markdown file #110
def save_to_markdown(prompt, response):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    prompt = prompt[:15]
    filename = f"{prompt}_response_{timestamp}.md"
    
    PATH = f"./save_history/{filename}"
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(f"**Prompt:**\n\n\n{prompt}\n\n\n")
        f.write(f"**Response:**\n\n{response}\n")

    print(f"\n✅ Response saved to: {PATH}")

def last_response(user_input, response):
    LAST_CHAT.clear()
    LAST_CHAT.append([{"role": "user", "content": user_input},{"role": "assistant", "content": response}])

while True:
    user_input = input("👤: ").strip()

    if user_input == "exit":
        break
    
    # Save to disk, last prompt, if user asked for with !save command #110
    if user_input == "!save":
        save_to_markdown(LAST_CHAT[0]['content'], LAST_CHAT[1]['content'])
        continue
    
    # Tools calling capability with decorators
    tool_response = call_tool_from_input(user_input)
    if tool_response:
        prompt = f"""
                    Use the most relevant memory snippet only to answer the user's question. Do not include unrelated or off-topic memory entries. \n

                    Tool `{tool_response['name']}` was called by the user. \n

                    Tool Output: \n
                    {tool_response['output']} \n

                    Now, based on this output, reply to the user meaningfully. \n
                    User Query: {user_input}
                """
        response = chat_with_model_stream("🛠", prompt)
        print("\n")
        last_response(user_input, response)
        continue

    if user_input.startswith("!remember"):
        note = user_input.replace("!remember", "").strip()
        emb = embed_text(note)

        # 🧠 Let bot extract tags from note
        auto_tags = extract_tags_from_query(note, MODEL_NAME)
        print(f"🏷️ Auto-tags used for memory: {auto_tags}")

        store.save_memory(note, tags=auto_tags, embedding=emb)
        print(f"📝 Memory saved. {auto_tags}")
        continue

    elif user_input.startswith("!recall"):
        query = user_input.replace("!recall", "").strip()
        q_emb = embed_text(query)
        results = store.search(q_emb)
        print("🔎 Found:")
        for r in results:
            print("- " + r)
        continue

    else:
        q_emb = embed_text(user_input)
        memories = store.search(q_emb)
        context = "\n".join(memories)

        prompt = f"Use the memory to help answer the user.\n\nMemory:\n{context}\n\nUser: {user_input}\nAI:"
        response = chat_with_model_stream("🤖", prompt)
        print("\n")

        ## Clear LAST_CHAT #110
        last_response(user_input, response)

