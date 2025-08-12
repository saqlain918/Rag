# app/rag/services.py
from app.rag.vector import VectorHandler, LLMHandler
from app.rag_emb.embedding import PDFEmbedder
from pydantic import BaseModel
from typing import List, Optional
import json


# Pydantic models for structured responses
class IntentClassification(BaseModel):
    Q: str  # Query meaning
    R: str  # Request meaning
    I: str  # Identified intent
    Reason: str  # Explanation


class SourceDocument(BaseModel):
    content: str
    relevance_score: Optional[float] = None
    page_number: Optional[int] = None


class RAGResponse(BaseModel):
    question: str
    answer: str
    intent: IntentClassification


class RAGService:
    def __init__(self):
        # Create embedder instance and ensure embedding is initialized
        self.pdf_embedder = PDFEmbedder()

        # Pass the initialized embedding to vector handler
        self.vector_handler = VectorHandler(self.pdf_embedder.embedding)
        self.llm_handler = LLMHandler()

    def run_intent_classification(self, user_message: str) -> IntentClassification:
        """Classify the intent of the user message and return structured data."""
        intent_json = self.llm_handler.classify_intent(user_message)

        try:
            # Clean the response - remove any formatting
            clean_json = intent_json.strip()
            if clean_json.startswith('```json'):
                clean_json = clean_json.replace('```json', '').replace('```', '')

            # Parse the JSON response
            intent_data = json.loads(clean_json)
            return IntentClassification(**intent_data)
        except (json.JSONDecodeError, TypeError) as e:
            # Fallback if JSON parsing fails
            return IntentClassification(
                Q="Query about information",
                R="Request for answer",
                I="general_query",
                Reason=f"JSON parsing failed, using fallback classification"
            )

    def answer_with_context(self, user_message: str) -> RAGResponse:
        """
        1. Retrieve context from Pinecone
        2. Pass it to Gemini LLM with structured output
        3. Return the structured RAG response
        """
        try:
            # Retrieve top documents
            docs = self.vector_handler.search(user_message, k=3)

            context = "\n\n".join([doc.page_content for doc in docs])
            has_context = bool(context.strip())

            # Get intent classification
            intent = self.run_intent_classification(user_message)

            if has_context:
                # Generate structured answer using context
                answer = self.llm_handler.generate_structured_answer(user_message, context)
            else:
                answer = "I don't have any relevant information in my knowledge base to answer this question."

            return RAGResponse(
                question=user_message,
                answer=answer,
                intent=intent
            )

        except Exception as e:
            # Return error response in proper format
            return RAGResponse(
                question=user_message,
                answer=f"Sorry, there was an error processing your question: {str(e)}",
                intent=IntentClassification(
                    Q="Error occurred",
                    R="System error",
                    I="error",
                    Reason="Exception during processing"
                )
            )