# Customer Support Chatbot

A new customer support chatbot project designed for professional, accurate, and helpful support interactions.

## Project Contents
- `customer_support_chatbot.py` - Python chatbot implementation with a structured prompt framework.
- `customer_support_prompt.md` - Prompt design and scenario templates for the chatbot.
- `requirements.txt` - Dependency list for the project.

## Setup
1. Open this folder in VS Code:
   ```bash
   code "C:\Users\rammi\OneDrive\Desktop\git hub\customer-support-chatbot"
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```powershell
   $env:OPENAI_API_KEY = "your_api_key_here"
   ```

## Run
Review a customer support query:
```bash
python customer_support_chatbot.py "My order is late and I need an update."
```

Run in interactive mode:
```bash
python customer_support_chatbot.py
```

## Notes
The chatbot uses a structured prompt template to:
- identify user intent
- provide step-by-step resolution
- maintain empathy and professionalism
- validate that the response solves the problem
