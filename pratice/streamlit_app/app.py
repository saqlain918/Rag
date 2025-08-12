import streamlit as st
import requests
import json

# Set Streamlit config
st.set_page_config(page_title="RAG Chatbot", layout="centered")

st.markdown("""
    <style>
        .chat-container {
            max-height: 450px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 10px;
            background-color: #1e1e1e;
            border: 1px solid #444;
            margin-bottom: 1rem;
        }

        .msg {
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            line-height: 1.6;
        }

        .user {
            background-color: #444;
            color: white;
        }

        .bot {
            background-color: #0077cc;
            color: white;
        }

        .intent-info {
            background-color: #2d2d2d;
            color: #cccccc;
            padding: 8px;
            border-radius: 5px;
            font-size: 0.85rem;
            margin-top: 5px;
            border-left: 3px solid #0077cc;
        }

        .title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }

        .upload-section {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🤖 RAG Chatbot with JSON Responses</div>', unsafe_allow_html=True)

# Sidebar for PDF upload
with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if st.button("Upload & Process") and uploaded_file is not None:
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post("http://localhost:8000/upload", files=files)

            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ Upload failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Settings
with st.expander("⚙️ Display Settings"):
    show_raw_json = st.checkbox("Show Raw JSON Response", value=False)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Track which messages have intent shown
if "show_intent_for" not in st.session_state:
    st.session_state.show_intent_for = set()

# Chat messages UI
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, msg in enumerate(st.session_state.chat_history):
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        # Intent toggle button
        if "intent" in msg and msg["intent"]:
            btn_label = "Hide Intent Analysis" if i in st.session_state.show_intent_for else "Show Intent Analysis"
            if st.button(btn_label, key=f"intent_btn_{i}"):
                if i in st.session_state.show_intent_for:
                    st.session_state.show_intent_for.remove(i)
                else:
                    st.session_state.show_intent_for.add(i)
                st.rerun()

            # Show intent above bot answer
            if i in st.session_state.show_intent_for:
                intent = msg["intent"]
                intent_html = f"""
                <div class="intent-info">
                    <strong>🎯 Intent Analysis:</strong><br>
                    <strong>Query:</strong> {intent.get('Q', 'N/A')}<br>
                    <strong>Request:</strong> {intent.get('R', 'N/A')}<br>
                    <strong>Intent:</strong> {intent.get('I', 'N/A')}<br>
                    <strong>Reason:</strong> {intent.get('Reason', 'N/A')}
                </div>
                """
                st.markdown(intent_html, unsafe_allow_html=True)

        # Bot message
        st.markdown(f'<div class="msg bot"><strong>Bot:</strong> {msg["answer"]}</div>', unsafe_allow_html=True)

        # Show raw JSON if enabled
        if show_raw_json and "raw_response" in msg:
            with st.expander("📋 Raw JSON Response"):
                st.code(json.dumps(msg["raw_response"], indent=2), language="json")
st.markdown('</div>', unsafe_allow_html=True)

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Ask something about your documents...",
                                   key="user_input",
                                   label_visibility="collapsed",
                                   placeholder="Type your question here...")
    with col2:
        submitted = st.form_submit_button("Send 🚀")

if submitted and user_input.strip():
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Send request to FastAPI backend
    try:
        payload = {"question": user_input}
        response = requests.post("http://localhost:8000/ask", json=payload)

        if response.status_code == 200:
            result = response.json()
            bot_reply = {
                "role": "bot",
                "answer": result.get("answer", "No answer returned."),
                "intent": result.get("intent", {}),
                "raw_response": result
            }
        else:
            bot_reply = {
                "role": "bot",
                "answer": f"Error: {response.status_code} - {response.text}",
                "intent": {},
                "raw_response": {}
            }
    except Exception as e:
        bot_reply = {
            "role": "bot",
            "answer": f"API Error: {str(e)}",
            "intent": {},
            "raw_response": {}
        }

    # Add bot response to history
    st.session_state.chat_history.append(bot_reply)

    # Rerun to show new message
    st.rerun()

# Footer with information
st.markdown("---")
st.markdown("""
### 📋 Features:
- **📄 PDF Upload**: Upload documents to build your knowledge base
- **🤖 Smart Responses**: Get AI-powered answers with intent analysis on demand  
- **🎯 Intent Classification**: Click the button above any answer to view analysis
- **📊 JSON Responses**: View raw structured responses
- **💬 Chat History**: Persistent conversation within session
""")

# Clear chat history button
if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.show_intent_for = set()
    st.rerun()
