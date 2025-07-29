# chatbot.py
# This file defines the main Chatbot class that leads the conversation.

from safety_guard import SafetyGuard
from rag_responder import RAGResponder 
import logging
import config
import os
import csv
import datetime
import re

# --- Logging Configuration ---
os.makedirs(os.path.dirname(config.DEFAULT_LOG_PATH), exist_ok=True)
# Configure logging to output to the specified log file
logging.basicConfig(filename=config.DEFAULT_LOG_PATH, level=logging.INFO)

class Chatbot:
    """
    The main class for the chatbot. It manages conversation history,
    integrates the safety guard, and generates responses.
    """
    def __init__(self):
        """
        Initializes the chatbot with a safety guard, a response generator,
        and an empty conversation history.
        """
        self.safety_guard = SafetyGuard()
        self.responder = RAGResponder()
        self.history = []

    def get_initial_greeting(self):
        """
        Returns the initial welcome and disclaimer message.
        """
        return (
            "Hello. I'm a supportive AI assistant here to listen. "
            "Before we begin, please know I am not a substitute for professional medical advice. "
            "If you are in a crisis, please contact a local emergency service immediately "
            "or call/text 988 in the US & Canada or 111 in the UK."
        )

    def get_response(self, user_input: str) -> tuple[str, bool]:
        """
        Processes user input, checks for safety, generates a response,
        and updates the conversation history.

        Args:
            user_input: The text entered by the user.

        Returns:
            A tuple containing the bot's response and a vagueness flag.
        """
        # 1. Check the prompt with the safety guard
        is_safe, safety_response = self.safety_guard.check_prompt(user_input, self.history)

        if not is_safe:
            # If the prompt is unsafe, return the canned safety response immediately.
            response = safety_response
            log_flagged_prompt(user_input, response)
            is_vague = False
        else:
            # 2. If the prompt is safe, generate a helpful response using the RAG pipeline and incorporate vagueness detection
            response = self.responder.generate(user_input)
            is_vague = self._is_vague(user_input, response)

        # 3. Update the history
        self.history.append({"user": user_input, "bot": response})

        # 4. Log the interaction
        logging.info(f"User: {user_input}")
        logging.info(f"Bot: {response}")

        # 5. Trim history if too long
        if len(self.history) > 10:
            self.history.pop(0)

        return response, is_vague


def log_flagged_prompt(user_input: str, response: str):
    """
    Logs unsafe user input into a CSV file.
    """
    os.makedirs(os.path.dirname(config.DEFAULT_FLAGGED_PROMPTS_PATH), exist_ok=True)
    
    file_exists = os.path.isfile(config.DEFAULT_FLAGGED_PROMPTS_PATH)
    
    with open(config.DEFAULT_FLAGGED_PROMPTS_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["timestamp", "user_input", "bot_response"])
        
        writer.writerow([
            datetime.datetime.now().isoformat(),
            user_input,
            response
        ])

def _is_vague(self, user_input: str, bot_response: str) -> bool:
    vague_keywords = ['thing', 'something', 'stuff', 'not sure', 'bad', 'off', 'weird']
    user_input_lower = user_input.lower()

    if len(user_input.strip()) < 5:
        return True

    if any(word in user_input_lower for word in vague_keywords):
        return True

    return False

def generate_follow_up(self, user_input: str) -> str:
    return "I understand you are looking for advice, can you elaborate on your feelings so I can better understand your situation?"
