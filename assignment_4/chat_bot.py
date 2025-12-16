import streamlit as st
import time

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chatbot")

# Streaming generator
def stream_text(text):
    for char in text:
        yield char
        time.sleep(0.05)

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
with st.sidebar :
    st.header("Settings")
    mode = st.selectbox("Select Mode",["Upper", "Lower", "Toggle"])
    count = st.slider("Message Count", 2,10,6,2)

# Chat input
user_msg = st.chat_input("Say something...")

if user_msg :
    if mode == "Upper":
        msg = user_msg.upper()
    elif mode == "Lower":
        msg = user_msg.lower()
    elif mode == "Toggle":
        msg = user_msg.swapcase()
if user_msg:
    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": msg
    })

    with st.chat_message("user"):
        st.write(msg)

    # Bot reply (echo logic)
    # bot_reply = user_msg.upper()

    # Stream bot reply
    with st.chat_message("assistant"):
        st.write_stream(stream_text(msg))

    # Store bot reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": msg
    })