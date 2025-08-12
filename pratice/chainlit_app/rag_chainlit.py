import chainlit as cl
import requests

API_URL = "http://localhost:8000"  # FastAPI backend URL

# -----------------------------------
# ✅ Plugin-style wrapper class
# -----------------------------------
class RAGPluginClient:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def upload_file(self, file_name: str, file_content: bytes) -> requests.Response:
        files = {
            "file": (file_name, file_content, "application/pdf")
        }
        return requests.post(f"{self.api_url}/upload", files=files)

    def ask_question(self, question: str) -> requests.Response:
        return requests.post(f"{self.api_url}/ask", params={"question": question})


# ✅ Create plugin client instance globally
rag_client = RAGPluginClient(API_URL)


@cl.on_chat_start
async def start_chat():
    # Ask user to upload a PDF file
    files = await cl.AskFileMessage(
        content="📄 Please upload your CV (PDF).",
        accept=["application/pdf"],
        max_size_mb=5,
        timeout=180,
    ).send()

    # ✅ Get the first uploaded file
    uploaded_file = files[0]

    # ✅ Read the file from the temp path Chainlit stores it at
    with open(uploaded_file.path, "rb") as f:
        file_content = f.read()

    try:
        # ✅ Use plugin to upload _file
        response = rag_client.upload_file(uploaded_file.name, file_content)
        if response.status_code == 200:
            await cl.Message("✅ File uploaded! You can now ask questions.").send()
        else:
            await cl.Message(f"❌ Upload failed ({response.status_code}).").send()
    except Exception as e:
        await cl.Message(f"❌ Upload error: {str(e)}").send()


@cl.on_message
async def handle_question(message: cl.Message):
    question = message.content.strip()

    try:
        # ✅ Use plugin to send the question
        response = rag_client.ask_question(question)

        if response.status_code == 200:
            answer = response.json().get("answer", "🤖 No answer found.")
            await cl.Message(answer).send()
        else:
            await cl.Message(f"❌ Failed to get response ({response.status_code}).").send()
    except Exception as e:
        await cl.Message(f"❌ Request error: {str(e)}").send()
