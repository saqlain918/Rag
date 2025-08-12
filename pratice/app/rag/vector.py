# app/rag/vector.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from app.config import GOOGLE_API_KEY, PINECONE_INDEX_NAME
import google.generativeai as genai
import json


class VectorHandler:
    def __init__(self, embedding_model):
        """
        embedding_model: Instance of GoogleGenerativeAIEmbeddings
                         passed from embedding.py so we reuse the same settings.
        """
        self.embedding_model = embedding_model
        self.vector_store = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=self.embedding_model
        )

    def search(self, query: str, k: int = 3):
        """Retrieve top-k most relevant documents from Pinecone."""
        return self.vector_store.similarity_search(query, k=k)


class LLMHandler:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        # Main LLM for RAG pipeline
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=GOOGLE_API_KEY
        )
        # Separate Gemini model for JSON responses
        self.structured_model = genai.GenerativeModel("gemini-1.5-flash")

    def get_llm(self):
        return self.llm

    def classify_intent(self, user_message: str) -> str:
        """Returns structured JSON with Q, R, I, Reason."""
        prompt = f"""
        You are an intent classification system.
        For the given message, classify it into:
        Q = Query meaning, R = Request meaning, I = Intent, Reason = Why you classified it that way.

        Output ONLY valid JSON format (no markdown, no explanation):
        {{
            "Q": "brief query meaning",
            "R": "brief request meaning", 
            "I": "identified_intent_category",
            "Reason": "brief explanation"
        }}

        Message: "{user_message}"
        """

        response = self.structured_model.generate_content(prompt)
        return response.text.strip()

    def generate_structured_answer(self, question: str, context: str) -> str:
        """Generate a comprehensive answer using the retrieved context."""
        prompt = f"""
        You are a helpful AI assistant. Use the following context to answer the user's question comprehensively.

        Guidelines:
        - Provide a detailed, informative answer
        - Use the context provided to support your response
        - If the context doesn't fully answer the question, mention what information is available
        - Be concise but thorough
        - Do not mention "based on the context" - just provide the answer naturally

        Context:
        {context}

        Question: {question}

        Answer:
        """

        response = self.structured_model.generate_content(prompt)
        return response.text.strip()

    def generate_json_response(self, question: str, context: str = None) -> str:
        """
        Generate a fully structured JSON response similar to Google GenAI example
        This is an alternative method for complete JSON output
        """
        if context:
            base_prompt = f"""
            Answer the following question using the provided context.
            Context: {context}
            Question: {question}
            """
        else:
            base_prompt = f"Answer this question: {question}"

        # This would be used if you want to implement Google's structured response format
        # You'll need to set up response_schema similar to the Google example
        response = self.structured_model.generate_content(base_prompt)
        return response.text