# knowledge_base.py

import google.generativeai as genai
import config
from datasets import load_dataset
import os
import pandas as pd
import json
import nltk
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
import re

# Ensure NLTK data is downloaded
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        print("NLTK 'punkt' already downloaded.")
    except LookupError:
        print("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt')
        print("NLTK 'punkt' downloaded.")

    try:
        nltk.data.find('sentiment/vader_lexicon')
        print("NLTK 'vader_lexicon' already downloaded.")
    except LookupError:
        print("Downloading NLTK 'vader_lexicon'...")
        nltk.download('vader_lexicon')
        print("NLTK 'vader_lexicon' downloaded.")
        
download_nltk_data()

genai.configure(api_key=config.GOOGLE_API_KEY)

os.environ["HF_HOME"] = "/tmp/huggingface_cache" # Ensure this path is clean/has space

EMBEDDINGS_FILE = config.DEFAULT_VECTOR_DB_PATH

# Initialize VADER for sentiment analysis
vader_analyzer = SentimentIntensityAnalyzer()

# --- Helper Functions for Metadata Extraction ---
def get_speaker(text: str) -> str:
    """Identifies the speaker based on common prefixes."""
    if text.strip().lower().startswith("client:"):
        return "Client"
    elif text.strip().lower().startswith("therapist:"):
        return "Therapist"
    return "Unknown"

def get_topic_keywords(text: str) -> list[str]:
    """
    Extracts simple topic keywords. For a real system, use NLP models (e.g., LDA, KeyBERT).
    This is a very basic example.
    """
    keywords = set()
    text_lower = text.lower()
    
    # Mental health specific keywords
    if "anxiety" in text_lower or "nervous" in text_lower:
        keywords.add("anxiety")
    if "depression" in text_lower or "sad" in text_lower or "hopeless" in text_lower:
        keywords.add("depression")
    if "stress" in text_lower or "overwhelmed" in text_lower:
        keywords.add("stress")
    if "coping" in text_lower or "manage" in text_lower:
        keywords.add("coping mechanisms")
    if "therapy" in text_lower or "counseling" in text_lower:
        keywords.add("therapy process")
    if "sleep" in text_lower or "insomnia" in text_lower:
        keywords.add("sleep issues")
    
    # You can expand this list significantly
    
    return list(keywords)

def get_emotional_tone(text: str) -> str:
    """
    Analyzes emotional tone using VADER sentiment analysis.
    Returns 'positive', 'neutral', 'negative', or 'mixed'.
    """
    vs = vader_analyzer.polarity_scores(text)
    if vs['compound'] >= 0.05:
        return "positive"
    elif vs['compound'] <= -0.05:
        return "negative"
    else:
        return "neutral" # VADER often marks very short or factual sentences as neutral
    
    # You could also add a 'mixed' if pos and neg are both high but compound is neutral
    # if vs['pos'] > 0.3 and vs['neg'] > 0.3 and abs(vs['compound']) < 0.05:
    #     return "mixed"
    # return "neutral" # Default if no strong sentiment


def generate_and_save_embeddings():
    """
    Generates embeddings for the knowledge base with recursive chunking and metadata,
    then saves them to a CSV file.
    """
    print("Loading dataset...")
    dataset = load_dataset("Amod/mental_health_counseling_conversations", split="train")
    print("Dataset loaded.")

    # Initialize the RecursiveCharacterTextSplitter
    # Use appropriate separators for conversational data
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.DEFAULT_CHUNK_SIZE,
        chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "! ", "? ", "\n\nClient:", "\n\nTherapist:", " "],
        length_function=len, # len measures characters. 
    )

    knowledge_base_data = []
    chunk_id_counter = 0

    print("Generating embeddings with chunking and metadata...")
    for i, sample in enumerate(dataset):
        original_source = f"Therapy Session #{i}"
        
        # Combine Context and Response into a single document string for chunking
        full_conversation_turn_content = f"Client: {sample['Context']}\nTherapist: {sample['Response']}"
        
        # Get metadata for the *entire* conversation turn (before chunking)
        # Some metadata might be more accurate at the larger document level
        overall_speaker_context = "Conversation" # Or "Mixed"
        overall_emotional_tone = get_emotional_tone(full_conversation_turn_content)
        overall_topic_keywords = get_topic_keywords(full_conversation_turn_content)

        # Split the full conversation turn into smaller chunks
        chunks = text_splitter.split_text(full_conversation_turn_content)
        
        if not chunks: # Handle cases where splitting might result in no chunks
            print(f"Warning: No chunks generated for Therapy Session #{i}. Skipping.")
            continue

        for j, chunk_text in enumerate(chunks):
            chunk_id_counter += 1
            
            # --- Extract Metadata for Each Chunk ---
            # You might want to refine how speaker/topic/tone are extracted for *each* chunk.
            # For simplicity, we'll try to extract for the chunk itself.
            
            chunk_speaker = get_speaker(chunk_text) # Might be "Client", "Therapist", or "Unknown" if mixed/partial
            chunk_emotional_tone = get_emotional_tone(chunk_text)
            chunk_topic_keywords = get_topic_keywords(chunk_text) # Re-evaluate keywords for smaller chunk

            metadata = {
                "source": original_source, # Original full document source
                "chunk_id": chunk_id_counter,
                "original_turn_index": i, # Which original therapy session it came from
                "chunk_index_in_turn": j, # Index of this chunk within its original turn
                "speaker": chunk_speaker,
                "emotional_tone": chunk_emotional_tone,
                "topic_keywords": json.dumps(chunk_topic_keywords), # Store as JSON string
                # Add any other relevant metadata here
            }

            try:
                embedding_response = genai.embed_content(
                    model=config.DEFAULT_GOOGLE_EMBEDDING_MODEL,
                    content=chunk_text, 
                    task_type="RETRIEVAL_DOCUMENT"
                )
                embedding = embedding_response['embedding']
                
                # Combine chunk content, embedding, and all metadata
                knowledge_base_data.append({
                    "content": chunk_text,
                    "embedding": json.dumps(embedding), # Store embedding as JSON string
                    **metadata # Unpack metadata dictionary
                })
                
            except Exception as e:
                print(f"Error embedding chunk {j} from Therapy Session #{i}: {e}. Content: {chunk_text[:100]}...")
                # Consider logging this or saving problematic chunks for review

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} original conversation turns...")

    print("Embeddings generated.")
    
    df = pd.DataFrame(knowledge_base_data)
    df.to_csv(EMBEDDINGS_FILE, index=False)
    print(f"Embeddings saved to {EMBEDDINGS_FILE}")

def load_embeddings_from_csv():
    """
    Loads embeddings and metadata from the CSV file.
    """
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"Embeddings file '{EMBEDDINGS_FILE}' not found. Generating them now...")
        generate_and_save_embeddings()
    
    print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
    df = pd.read_csv(EMBEDDINGS_FILE)
    
    # Convert 'embedding' and 'topic_keywords' strings back to lists/objects
    df['embedding'] = df['embedding'].apply(json.loads)
    df['topic_keywords'] = df['topic_keywords'].apply(json.loads)
    
    print("Embeddings loaded.")
    return df.to_dict(orient='records')

KNOWLEDGE_BASE_EMBEDDINGS = load_embeddings_from_csv()

if __name__ == "__main__":
    # If this script is run directly, it will regenerate and save embeddings.
    # Otherwise, it will load when imported by main.py.
    generate_and_save_embeddings()
    print("Embeddings generated.")
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(knowledge_base_data)
    df.to_csv(EMBEDDINGS_FILE, index=False) # index=False prevents writing the DataFrame index as a column
    print(f"Embeddings saved to {EMBEDDINGS_FILE}")

def load_embeddings_from_csv():
    """
    Loads embeddings from the CSV file.
    """
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"Embeddings file '{EMBEDDINGS_FILE}' not found. Generating them now...")
        generate_and_save_embeddings()
    
    print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
    df = pd.read_csv(EMBEDDINGS_FILE)
    
    # Convert the 'embedding' string back to a list of floats
    df['embedding'] = df['embedding'].apply(json.loads)
    
    print("Embeddings loaded.")
    return df.to_dict(orient='records') # Convert DataFrame back to list of dictionaries

# This is the global variable that rag_responder.py will import
KNOWLEDGE_BASE_EMBEDDINGS = load_embeddings_from_csv()

# You can add a main guard to only run generation if this script is executed directly
if __name__ == "__main__":
    # If you run `python knowledge_base.py`, it will generate and save
    # If `main.py` is run, it will call load_embeddings_from_csv which will
    # generate if the file doesn't exist.
    pass