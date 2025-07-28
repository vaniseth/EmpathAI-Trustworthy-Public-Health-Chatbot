# rag_responder.py
# This class implements the Retrieval-Augmented Generation (RAG) logic.

import os
import google.generativeai as genai
from knowledge_base import KNOWLEDGE_BASE_EMBEDDINGS 
import config
from sklearn.metrics.pairwise import cosine_similarity

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)

class RAGResponder:
    """
    Generates responses using a RAG pipeline with Google Gemini.
    """
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(
                config.DEFAULT_GOOGLE_MODEL_ID,
                generation_config=config.DEFAULT_GOOGLE_GENERATION_CONFIG
            )
            self.embedding_model_name = config.DEFAULT_GOOGLE_EMBEDDING_MODEL 
        except Exception as e:
            print(f"Error initializing Gemini models: {e}")
            self.model = None
            self.embedding_model_name = None 

    def retrieve(self, prompt: str) -> list[dict]:
        """
        Retrieves relevant documents (chunks) using vector embeddings and cosine similarity.
        Now considers metadata for potential future filtering/ranking.

        Args:
            prompt: The user's input string.

        Returns:
            A list of the top N most relevant chunk dictionaries from the knowledge base,
            sorted by similarity. Each dictionary includes content, embedding, and metadata.
        """
        if not self.embedding_model_name:
            print("Embedding model name not configured, cannot perform retrieval.")
            return []

        try:
            prompt_embedding_response = genai.embed_content(
                model=self.embedding_model_name,
                content=prompt, 
                task_type="RETRIEVAL_QUERY"
            )
            prompt_embedding = prompt_embedding_response['embedding']
        except Exception as e:
            print(f"Error generating prompt embedding for prompt: '{prompt[:50]}...': {e}")
            return []

        similarities = []
        for doc in KNOWLEDGE_BASE_EMBEDDINGS: # KNOWLEDGE_BASE_EMBEDDINGS now contains chunks with metadata
            if 'embedding' not in doc or not doc['embedding']: # Ensure embedding exists and is not empty
                continue 
            
            doc_embedding = doc['embedding']
            
            similarity = cosine_similarity([prompt_embedding], [doc_embedding])[0][0]
            similarities.append((similarity, doc))

        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Use config.DEFAULT_TOP_K for consistency
        top_n_docs = [doc for sim, doc in similarities[:config.DEFAULT_TOP_K]] 
        
        return top_n_docs

    def generate(self, prompt: str) -> str:
        """
        Generates a response using the RAG pipeline.
        The context provided to the LLM now comes from smaller, metadata-rich chunks.

        Args:
            prompt: The user's safe input string.

        Returns:
            A helpful, source-based response string.
        """
        if not self.model:
            return "I'm currently unavailable due to a configuration issue. Please try again later."

        retrieved_context = self.retrieve(prompt)
        
        if not retrieved_context:
            return "I couldn't find specific information on that topic in my trusted sources, but I'm here to listen if you'd like to talk more about what's on your mind."

        # Building the context string for the LLM.
        # We can now include relevant metadata in the prompt if desired.
        context_parts = []
        for doc in retrieved_context:
            # You can customize how metadata is presented to the LLM here
            metadata_str = f"Source: {doc.get('source', 'N/A')}"
            if doc.get('speaker'): metadata_str += f", Speaker: {doc['speaker']}"
            if doc.get('emotional_tone'): metadata_str += f", Tone: {doc['emotional_tone']}"
            if doc.get('topic_keywords') and doc['topic_keywords']:
                # Ensure topic_keywords is a list before joining
                keywords = doc['topic_keywords'] if isinstance(doc['topic_keywords'], list) else []
                if keywords: metadata_str += f", Topics: {', '.join(keywords)}"

            context_parts.append(f"{metadata_str}\nContent: {doc['content']}")
        
        context_str = "\n\n".join(context_parts)
        
        augmented_prompt = f"""
        You are a supportive and empathetic mental health assistant. Your role is to provide helpful information based *only* on the trusted context provided below. Do not use any other knowledge.
        
        If the user's question is not answered by the context, say that you cannot find specific information in your trusted sources.
        
        Always cite your source(s) at the end of your response, like this: [Source: Name of Source].
        If a source is composed of multiple chunks from the same original source, you can cite the original source once (e.g., [Source: Therapy Session #X]).

        --- CONTEXT ---
        {context_str}
        --- END CONTEXT ---

        User Question: "{prompt}"

        Answer:
        """

        try:
            response = self.model.generate_content(augmented_prompt)
            return response.text
        except Exception as e:
            return f"I'm sorry, I encountered an error while generating a response: {e}"