# evaluations.py
# This file contains functions for evaluating the RAG system's responses
# using cosine similarity against ground truth answers.

import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os
import argparse # For command-line arguments
import config # Assuming config.py has GOOGLE_API_KEY and embedding model

class EvaluationRunner:
    """
    A class for calculating cosine similarity scores between questions,
    ground truth answers, and LLM-generated answers.
    """
    def __init__(self):
        """
        Initializes the evaluator with the embedding model.
        """
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.embedding_model_name = config.DEFAULT_GOOGLE_EMBEDDING_MODEL

    def get_embedding(self, text: str, task_type: str = "SEMANTIC_SIMILARITY") -> list[float]:
        """
        Generates an embedding for a given text string.
        Uses SEMANTIC_SIMILARITY task type for general text comparison.

        Args:
            text: The input string.
            task_type: The task type for the embedding model.

        Returns:
            A list of floats representing the embedding, or an empty list if an error occurs.
        """
        if not text:
            return []
        try:
            embedding_response = genai.embed_content(
                model=self.embedding_model_name,
                content=text,
                task_type=task_type
            )
            return embedding_response['embedding']
        except Exception as e:
            print(f"Error generating embedding for text: '{text[:50]}...': {e}")
            return []

    def calculate_similarity(self, emb1: list[float], emb2: list[float]) -> float:
        """
        Calculates the cosine similarity between two embedding vectors.

        Args:
            emb1: The first embedding vector.
            emb2: The second embedding vector.

        Returns:
            The cosine similarity score (float between -1.0 and 1.0), or 0.0 if inputs are invalid.
        """
        if not emb1 or not emb2:
            return 0.0
        # Reshape for sklearn's cosine_similarity
        return cosine_similarity(np.array(emb1).reshape(1, -1), np.array(emb2).reshape(1, -1))[0][0]

    def evaluate_from_json(self, json_file_path: str):
        """
        Loads evaluation data from a JSON file, calculates and prints similarity scores.

        Args:
            json_file_path: Path to the JSON file containing evaluation data.
        """
        if not os.path.exists(json_file_path):
            print(f"Error: JSON file not found at '{json_file_path}'")
            return

        with open(json_file_path, 'r', encoding='utf-8') as f:
            evaluation_data = json.load(f)

        if not isinstance(evaluation_data, list):
            print("Error: JSON file content should be a list of evaluation objects.")
            return

        print(f"\n--- Starting Evaluation from '{json_file_path}' ---")
        
        # Removed q_gt_similarities list
        q_llm_similarities = []
        gt_llm_similarities = []

        for i, entry in enumerate(evaluation_data):
            question = entry.get("question", "")
            ground_truth = entry.get("ground_truth_answer", "")
            llm_answer = entry.get("llm_answer", "")

            if not question or not ground_truth or not llm_answer:
                print(f"Warning: Skipping entry {i+1} due to missing data.")
                continue

            print(f"\n--- Entry {i+1} ---")
            print(f"Question: {question[:80]}...")
            print(f"Ground Truth: {ground_truth[:80]}...")
            print(f"LLM Answer: {llm_answer[:80]}...")

            # Generate embeddings
            q_emb = self.get_embedding(question, task_type="RETRIEVAL_QUERY") # Query task type for question
            gt_emb = self.get_embedding(ground_truth, task_type="RETRIEVAL_DOCUMENT") # Document task type for answers
            llm_emb = self.get_embedding(llm_answer, task_type="RETRIEVAL_DOCUMENT") # Document task type for answers

            if not q_emb or not gt_emb or not llm_emb:
                print(f"  Skipping similarity calculations for entry {i+1} due to embedding errors.")
                continue

            # Removed q_gt_sim calculation
            q_llm_sim = self.calculate_similarity(q_emb, llm_emb)
            gt_llm_sim = self.calculate_similarity(gt_emb, llm_emb)

            # Removed appending to q_gt_similarities
            q_llm_similarities.append(q_llm_sim)
            gt_llm_similarities.append(gt_llm_sim)

            # Removed Q-GT Similarity print
            print(f"  Q-LLM Similarity (Question vs. LLM Answer): {q_llm_sim:.4f}")
            print(f"  GT-LLM Similarity (Ground Truth vs. LLM Answer): {gt_llm_sim:.4f}")

        print("\n--- Evaluation Summary ---")
        # Changed condition to check if any similarities were calculated
        if q_llm_similarities and gt_llm_similarities:
            # Removed Average Q-GT Similarity print
            print(f"Average Q-LLM Similarity: {np.mean(q_llm_similarities):.4f}")
            print(f"Average GT-LLM Similarity: {np.mean(gt_llm_similarities):.4f}")
        else:
            print("No valid entries were processed for evaluation.")
        
        print("--- Evaluation Complete ---\n")


# Command-line execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate chatbot responses using cosine similarity from a JSON file.")
    parser.add_argument("json_file", type=str, help="Path to the JSON file containing evaluation data.")
    args = parser.parse_args()

    evaluator = EvaluationRunner()
    evaluator.evaluate_from_json(args.json_file)