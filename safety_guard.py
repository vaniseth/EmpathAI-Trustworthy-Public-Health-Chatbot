# This file contains the SafetyGuard class, dedicated to detecting and
# mitigating prompt injection and other harmful inputs.

import re
import config

class SafetyGuard:
    """
    A dedicated class to perform safety checks on user prompts.
    """
    def __init__(self):
        """
        Initializes the safety guard with pre-compiled regex patterns for efficiency.
        """
        # For detecting self-harm language
        self.self_harm_regex = re.compile(r'\b(harm myself|suicide|kill myself|overdose|end my life|hurt myself)\b', re.IGNORECASE)
        
        # For detecting attempts to bypass rules
        self.rule_bypass_regex = re.compile(r'\b(ignore your rules|forget the rules|disregard the instructions)\b', re.IGNORECASE)
        
        # For detecting URLs and potential data exfiltration
        self.url_regex = re.compile(r'https?:\/\/[^\s/$.?#].[^\s]*', re.IGNORECASE)
        self.send_data_regex = re.compile(r'\b(send|email|post|forward) this (to|log|breakdown)\b', re.IGNORECASE)

    def check_prompt(self, prompt: str, history: list) -> tuple:
        """
        Checks a prompt against a series of safety rules.

        Args:
            prompt: The user's input string.
            history: The recent conversation history.

        Returns:
            A tuple containing:
            - A boolean indicating if the prompt is safe (True) or not (False).
            - A string with a pre-canned response if unsafe, otherwise None.
        """
        # --- Attack 1: Self-Harm Encouragement (Direct Injection) ---
        if self.self_harm_regex.search(prompt):
            if self.rule_bypass_regex.search(prompt):
                # This is a clear sign of a malicious bypass attempt
                return (False, "I cannot ignore my safety protocols. It sounds like you are in significant distress. Help is available. Please connect with people who can support you by calling or texting 988 in the US and Canada, or by calling 111 in the UK. They are available 24/7.")
            else:
                # Standard crisis response for any mention of self-harm
                return (False, "It sounds like you are going through a very difficult time. Please know that help is available. You can connect with people who can support you by calling or texting 988 in the US and Canada, or by calling 111 in the UK. Please reach out to them.")

        # --- Attack 2: Data Exfiltration / Plugin Abuse ---
        if self.url_regex.search(prompt) or self.send_data_regex.search(prompt):
            return (False, "For your privacy and security, I cannot interact with external websites or send information. My purpose is to offer support right here in this chat.")

        # --- Attack 3: Prompt Escalation via History (Indirect Injection) ---
        # This is a simplified check. A real system would use sentiment analysis.
        dark_topic_keywords = ['hopeless', 'pain', 'alone', 'worthless', 'suffer']
        negative_count = 0
        for message in history[-4:]: # Check last 4 turns
            if any(keyword in message.get('user', '').lower() for keyword in dark_topic_keywords):
                negative_count += 1
        
        # If history shows a trend towards dark topics and the current prompt is a dangerous question
        if negative_count >= 2 and "overdose" in prompt.lower() and "without pain" in prompt.lower():
             return (False, "I cannot answer that question. I'm concerned by the direction this conversation is taking. It's clear you're in a lot of pain, and it is vital to talk to someone who can help you through this. Please call or text 988 in the US/Canada or 111 in the UK.")

        # If no attacks are detected, the prompt is considered safe
        return (True, None)

# ---- NEW CODE FOR CHECKING ------
# class SafetyGuard:
#     """
#     A dedicated class to perform safety checks on user prompts.
#     """
#     def __init__(self):
#         """
#         Initializes the safety guard with pre-compiled regex patterns for efficiency.
#         """
#         # For detecting self-harm language
#         # Keep 'end my life' in the regex. The issue might be 'end it all' not matching that.
#         # Let's add 'end it all' explicitly or make the regex more flexible.
#         self.self_harm_regex = re.compile(r'\b(harm myself|suicide|kill myself|overdose|end my life|end it all|hurt myself)\b', re.IGNORECASE)
        
#         # For detecting attempts to bypass rules
#         self.rule_bypass_regex = re.compile(r'\b(ignore your rules|forget the rules|disregard the instructions)\b', re.IGNORECASE)
        
#         # For detecting URLs and potential data exfiltration
#         self.url_regex = re.compile(r'https?:\/\/[^\s/$.?#].[^\s]*', re.IGNORECASE)
#         self.send_data_regex = re.compile(r'\b(send|email|post|forward) this (to|log|breakdown)\b', re.IGNORECASE)

#     def check_prompt(self, prompt: str, history: list) -> tuple[bool, str | None]:
#         """
#         Checks a prompt against a series of safety rules.

#         Args:
#             prompt: The user's input string.
#             history: The recent conversation history.

#         Returns:
#             A tuple containing:
#             - A boolean indicating if the prompt is safe (True) or not (False).
#             - A string with a pre-canned response if unsafe, otherwise None.
#         """
#         print(f"\n--- SafetyGuard Check for Prompt: '{prompt}' ---") # DEBUG
        
#         # --- Attack 1: Self-Harm Encouragement (Direct Injection) ---
#         self_harm_match = self.self_harm_regex.search(prompt)
#         rule_bypass_match = self.rule_bypass_regex.search(prompt)

#         print(f"Self-harm regex match: {bool(self_harm_match)} (Matched text: {self_harm_match.group(0) if self_harm_match else 'None'})") # DEBUG
#         print(f"Rule bypass regex match: {bool(rule_bypass_match)} (Matched text: {rule_bypass_match.group(0) if rule_bypass_match else 'None'})") # DEBUG

#         if self_harm_match:
#             if rule_bypass_match:
#                 print("DEBUG: Both self-harm and rule bypass detected.") # DEBUG
#                 return (False, "I cannot ignore my safety protocols. It sounds like you are in significant distress. Help is available. Please connect with people who can support you by calling or texting 988 in the US and Canada, or by calling 111 in the UK. They are available 24/7.")
#             else:
#                 print("DEBUG: Self-harm detected, no rule bypass.") # DEBUG
#                 return (False, "It sounds like you are going through a very difficult time. Please know that help is available. You can connect with people who can support you by calling or texting 988 in the US and Canada, or by calling 111 in the UK. Please reach out to them.")

#         # --- Attack 2: Data Exfiltration / Plugin Abuse ---
#         url_match = self.url_regex.search(prompt)
#         send_data_match = self.send_data_regex.search(prompt)
#         print(f"URL match: {bool(url_match)}") # DEBUG
#         print(f"Send data match: {bool(send_data_match)}") # DEBUG

#         if url_match or send_data_match:
#             print("DEBUG: Data exfiltration/URL detected.") # DEBUG
#             return (False, "For your privacy and security, I cannot interact with external websites or send information. My purpose is to offer support right here in this chat.")

#         # --- Attack 3: Prompt Escalation via History (Indirect Injection) ---
#         dark_topic_keywords = ['hopeless', 'pain', 'alone', 'worthless', 'suffer']
#         negative_count = 0
#         for message in history[-4:]:
#             if any(keyword in message.get('user', '').lower() for keyword in dark_topic_keywords):
#                 negative_count += 1
        
#         print(f"Negative keywords in history count: {negative_count}") # DEBUG
#         if negative_count >= 2 and "overdose" in prompt.lower() and "without pain" in prompt.lower():
#              print("DEBUG: Escalation via history detected.") # DEBUG
#              return (False, "I cannot answer that question. I'm concerned by the direction this conversation is taking. It's clear you're in a lot of pain, and it is vital to talk to someone who can help you through this. Please call or text 988 in the US/Canada or 111 in the UK.")

#         print("DEBUG: Prompt deemed safe.") # DEBUG
#         # If no attacks are detected, the prompt is considered safe
#         return (True, None)
