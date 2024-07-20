import os

from langchain_openai import ChatOpenAI

class LLMConfiguration:
    temperature=1.0
    max_tokens=150
    text_generation_timeout=600

    def __init__(self, config):
        self.model_name = os.environ.get('OPENAI_MODEL_NAME')
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.api_base = os.environ.get('OPENAI_API_BASE')
        self.temperature = config["temperature"]
        self.frequency_penalty = config["frequency_penalty"]
        self.presence_penalty = config["presence_penalty"]
        self.max_tokens = config["max_tokens"]
        self.text_generation_timeout = config["text_generation_timeout"]

    def chat_model(self):
        model = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            verbose=True,
            temperature=self.temperature,
            timeout=self.text_generation_timeout,
            max_tokens=self.max_tokens,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            streaming=True,
            stop=["<|end_of_text|>"],
            # model_kwargs={"stop": ["<|user|>"]}
        )
        return model