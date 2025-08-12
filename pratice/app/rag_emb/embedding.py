# app/rag_emb/embedding.py - Fixed version
import os
from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from app.config import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX_NAME, GOOGLE_API_KEY


class PDFEmbedder:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Initialize embedding immediately
        self.embedding = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        self.pinecone = None

    def _init_pinecone(self):
        if not self.pinecone:
            self.pinecone = Pinecone(api_key=PINECONE_API_KEY)
            # Create index if it doesn't exist
            if PINECONE_INDEX_NAME not in [index.name for index in self.pinecone.list_indexes()]:
                self.pinecone.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=768,  # Gemini embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
                )

    def load_texts(self):
        texts = []
        for file in os.listdir(self.data_dir):
            if file.endswith(".pdf"):
                path = os.path.join(self.data_dir, file)
                reader = PdfReader(path)
                text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
                if text.strip():
                    texts.append(text)
        return texts

    def split_texts(self, texts):
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.create_documents(texts)

    def process_and_store(self):
        # Initialize Pinecone when needed
        self._init_pinecone()

        raw_texts = self.load_texts()
        if not raw_texts:
            raise ValueError("No PDF content found in data directory.")

        docs = self.split_texts(raw_texts)

        PineconeVectorStore.from_documents(
            documents=docs,
            embedding=self.embedding,
            index_name=PINECONE_INDEX_NAME,
        )