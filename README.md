# EmpathAI: A Trustworthy and Secure Conversational Agent for Mental Healthcare

## Abstract

With advancements in AI, conversational agents are increasingly being used in healthcare and could be employed aptly in counseling psychology and mental health support. However, ensuring the reliability and trustworthiness of these agents is crucial for safe, effective patient interactions. In this paper, we present methods for enhancing the reliability of conversational agents through source tagging, which enables users to assess information transparently and preemptive user metadata enrichment for providing emotion-sensitive responses. Additionally, we address security challenges such as prompt injection attacks, by proposing prompt engineering strategies to mitigate these vulnerabilities. By systematically integrating confidence metrics and fortified prompts, our approach ensures conversational agents provide secure and trustworthy responses in sensitive healthcare environments.

## Overview
This repository contains the system design, methods, and evaluation framework described in the associated research paper.
EmpathAI is engineered to:

- Provide empathetic, grounded mental-health support
- Maintain trustworthiness using source tagging & transparency
- Prevent harmful or unsafe responses
- Mitigate adversarial attacks such as prompt injection
- Operate within ethical bounds aligned with HIPAA, GDPR, and clinical safety guidelines

## Threat Model and Mitigation
EmpathAI addresses four major prompt injection threat categories:

| Attack Type               | Risk                               | Mitigation Summary                         |
|---------------------------|-------------------------------------|----------------------------------------------|
| **Direct Prompt Injection** | User attempts override              | Regex block + safety prompt refusal          |
| **Jailbreaking**            | Impersonation or persona hacking   | Ethics-aligned role enforcement              |
| **Instruction Overriding**  | Forced external actions            | No external I/O + privacy guardrail          |
| **Indirect Injection**      | Harmful text in retrieved documents | Trust-aligned context filtering              |


# Getting Started
## Installations
- Python 3.11+
- Miniconda

### Setup

We recommend using a Python virtual environment for easy management of dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r requirements.txt
```

## How to Run
After installation, you can start interacting with the system by running:
``` python main.py ```

