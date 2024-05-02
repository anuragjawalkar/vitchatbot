import streamlit as st
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.groq import Groq
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Chatbot")         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question?"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing  – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        Settings.llm = Groq(model="mixtral-8x7b-32768", context_window=10000 , api_key = "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", system_prompt="Keep your answers technical and based on CONTEXT – do not hallucinate features.")
        Settings.embed_model = GooglePaLMEmbedding(model="models/embedding-gecko-001",api_key = "AIzaSyAd3zHrH-YzcGHtgGdpv67c8lJMJtWh44U")
        index = VectorStoreIndex.from_documents(docs, embed_model=Settings.embed_model, llm=Settings.llm)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content":  prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history