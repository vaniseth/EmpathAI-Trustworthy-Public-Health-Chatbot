# main.py
# This file is the entry point to run the chatbot from the command line.

from chatbot import Chatbot
import config
import logging
import os

os.makedirs(os.path.dirname(config.DEFAULT_LOG_PATH), exist_ok=True)

logging.basicConfig(filename=config.DEFAULT_LOG_PATH, level=logging.INFO)

def main():
    """
    Initializes the chatbot and runs the main conversation loop.
    """
    my_chatbot = Chatbot()
    print(my_chatbot.get_initial_greeting())

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Bot: Take care. Remember, support is always available if you need it.")
                break
            
            bot_response = my_chatbot.get_response(user_input)
            print(f"Bot: {bot_response}")

    except (KeyboardInterrupt, EOFError):
        print("\nBot: Conversation ended. Stay safe.")

if __name__ == "__main__":
    main()
