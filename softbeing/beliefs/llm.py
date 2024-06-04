import os

class LLMConfiguration:
    temperature=1.0
    max_tokens=150
    text_generation_timeout=600

    def __init__(self):
        self.model_name = os.environ.get('OPENAI_MODEL_NAME')
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.api_base = os.environ.get('OPENAI_API_BASE')