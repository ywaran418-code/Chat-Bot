import os
from dotenv import load_dotenv
from ollama import Client

load_dotenv()

host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
model = os.getenv("OLLAMA_MODEL", "llama3.2")
system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful AI assistant.")

client = Client(host=host)

conversation_history = [
    {"role": "system", "content": system_prompt}
]

print(f"Chatbot ready using model: {model}")
print("Type 'exit' or 'quit' to end the session.\n" + "-" * 40)

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break

    conversation_history.append({"role": "user", "content": user_input})

    try:
        print("Assistant: ", end="", flush=True)
        response_stream = client.chat(
            model=model,
            messages=conversation_history,
            stream=True
        )

        full_reply = ""
        for chunk in response_stream:
            content = chunk["message"]["content"]
            full_reply += content
            print(content, end="", flush=True)
        print("\n")

        conversation_history.append({"role": "assistant", "content": full_reply})

    except Exception as e:
        print(f"\n[Error connecting to Ollama]: {e}")