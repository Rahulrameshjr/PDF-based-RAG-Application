import streamlit as st
import requests
import os
import subprocess
import sys

# Page config
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PDF RAG Chatbot")
st.markdown("Upload a PDF and ask questions based on its content.")

API_URL = "http://127.0.0.1:8000"

def get_collections():
    try:
        response = requests.get(f"{API_URL}/collections")
        if response.status_code == 200:
            return response.json().get("collections", [])
    except:
        return []
    return []

# Sidebar
with st.sidebar:
    st.header("📁 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save uploaded file
        pdf_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("🔄 Process PDF", use_container_width=True):
            with st.spinner("Processing PDF... this may take a few minutes."):
                try:
                    # Run ingest script
                    result = subprocess.run(
                        [sys.executable, "ingest.py", pdf_path],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("✅ PDF processed successfully!")
                        st.session_state.pdf_processed = True
                        st.rerun()
                    else:
                        st.error(f"Error: {result.stderr}")
                except Exception as e:
                    st.error(f"Failed: {str(e)}")

    st.divider()

    # Document selector
    st.header("📚 Select Document")
    collections = get_collections()

    if collections:
        selected_collection = st.selectbox(
            "Choose a document to query:",
            options=collections,
            index=0
        )
        st.session_state.selected_collection = selected_collection
        st.info(f"Active: **{selected_collection}**")
    else:
        st.warning("No documents processed yet. Upload and process a PDF first.")
        st.session_state.selected_collection = None

    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Upload a PDF")
    st.markdown("2. Click Process PDF")
    st.markdown("3. Select document")
    st.markdown("4. Ask questions below")

# Chat area
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show active document
if st.session_state.get("selected_collection"):
    st.markdown(f"💬 Chatting with: **{st.session_state.selected_collection}**")
else:
    st.warning("Please upload and select a document from the sidebar to start chatting.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.caption(f"📖 Sources (pages): {message['sources']}")

# Chat input
if question := st.chat_input("Ask a question about your PDF..."):
    if not st.session_state.get("selected_collection"):
        st.error("Please select a document first!")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={
                            "question": question,
                            "collection_name": st.session_state.selected_collection
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        sources = data.get("sources", [])

                        st.markdown(answer)
                        if sources:
                            st.caption(f"📖 Sources (pages): {sources}")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        st.error("Failed to get answer from API.")
                except Exception as e:
                    st.error(f"Make sure FastAPI server is running! Error: {str(e)}")