

# EmpathAI: A Trustworthy RAG Chatbot for Mental Health Support

## Overview

EmpathAI is a Retrieval-Augmented Generation (RAG) based chatbot designed to provide supportive and empathetic responses in the domain of mental health. This project focuses on building a trustworthy AI system by implementing robust data processing techniques, multi-layered safety guardrails, and clear evaluation methodologies. The chatbot leverages a curated knowledge base derived from therapeutic conversations to ensure its responses are grounded, relevant, and safe.

## Features

* **Retrieval-Augmented Generation (RAG) Pipeline:** Integrates a powerful RAG mechanism to retrieve relevant information from a specialized knowledge base, minimizing hallucinations and grounding responses in factual or conversational patterns.
* **Rich Metadata Extraction:** Each knowledge chunk is enriched with metadata such as:

  * **Generalized Source:** Indicates the origin from "therapeutic conversations" for transparency without compromising privacy.
  * **Speaker Identification:** Distinguishes between "Client" and "Therapist" segments.
  * **Emotional Tone:** Analyzed using VADER sentiment to inform empathetic responses.
  * **Topic Keywords:** Provides thematic tags for enhanced semantic retrieval.
* **Multi-layered Prompt Injection Mitigation:**

  * **Regex-based Filtering:** A pre-processing module that uses regular expressions to detect and block explicit harmful inputs (e.g., self-harm ideation, rule-bypass attempts, data exfiltration requests) before they reach the LLM.
  * **Robust Prompt Engineering:** Implements a "sandwich defense" strategy within the LLM's system prompt, explicitly defining the chatbot's persona, non-negotiable safety rules, and instructions to prioritize system directives over conflicting user inputs

## How to run the code

1. Clone the Repository

   ```bash
   git clone <https://github.com/vaniseth/Trustworthy-Public-Health-Chatbot.git>
   cd EmpathAI
   ```
2. Create a Virtual Environment and install libraries

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the chatbot

```bash
python main.py
```

4. Run evalutions

   ```bash
   python evaluations.py evaluation_data.json
   ```
