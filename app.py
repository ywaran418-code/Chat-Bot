import streamlit as st
from ollama import Client

st.set_page_config(
    page_title="Llama 3.2 Chatbot", page_icon="🦙", layout="centered"
)
st.title("🦙 Llama 3.2 Local Assistant")

# Sidebar
with st.sidebar:
  st.header("Settings")
  user_email = st.text_input("User Email", placeholder="user@example.com")
  temperature = st.slider(
      "Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05
  )

  if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

client = Client(host="http://localhost:11434")
MODEL_NAME = "llama3.2"

if "messages" not in st.session_state:
  st.session_state.messages = []


# Helper function to extract plain text string
def extract_text(content):
  if isinstance(content, str):
    return content
  elif isinstance(content, list):
    # Extracts text if content is formatted like [{'text': '...', 'type': 'text'}]
    parts = []
    for item in content:
      if isinstance(item, dict) and "text" in item:
        parts.append(item["text"])
      elif isinstance(item, str):
        parts.append(item)
    return " ".join(parts)
  elif isinstance(content, dict) and "text" in content:
    return content["text"]
  return str(content)


# Render existing messages
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(extract_text(msg["content"]))

# Capture input
if raw_input := st.chat_input("Type your message here..."):
  # Extract string even if chat_input passes a complex object
  user_text = (
      raw_input.text
      if hasattr(raw_input, "text")
      else (raw_input if isinstance(raw_input, str) else extract_text(raw_input))
  )

  # Append clean string to session state
  st.session_state.messages.append({"role": "user", "content": user_text})
  with st.chat_message("user"):
    st.markdown(user_text)

  # Prepare sanitized message history for Ollama
  system_instruction = (
      "You are a helpful assistant. The logged-in user is"
      f" {user_email or 'Guest'}."
  )
  ollama_payload = [{"role": "system", "content": system_instruction}]

  for msg in st.session_state.messages:
    ollama_payload.append(
        {"role": msg["role"], "content": extract_text(msg["content"])}
    )

  # Stream assistant response
  with st.chat_message("assistant"):

    def response_generator():
      try:
        stream = client.chat(
            model=MODEL_NAME,
            messages=ollama_payload,
            stream=True,
            options={"temperature": temperature},
        )
        for chunk in stream:
          content = chunk.get("message", {}).get("content", "")
          yield content
      except Exception as e:
        yield f"⚠️ Ollama Connection Error: {e}"

    response_text = st.write_stream(response_generator())

  st.session_state.messages.append(
      {"role": "assistant", "content": response_text}
  )