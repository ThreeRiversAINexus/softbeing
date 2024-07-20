from dotenv import load_dotenv

from softbeing.beliefs import LLMConfiguration, PersonalityConfiguration
from softbeing.utils import ConfigLoader

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.chat_message_histories import ChatMessageHistory

class SoftbeingBasicCLIAgent:
    def __init__(self, config):
        self.config = config
        self.llm_config = LLMConfiguration(config["llm_configuration"])
        self.identity = PersonalityConfiguration(config["personality_configuration"])

    def simple_chat_prompt_template(self, system_prompt):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 system_prompt),
                 MessagesPlaceholder(variable_name="messages")
            ]
        )
        return prompt

    def create_chat_chain(self):
        system_prompt = """
        You are an AI assistant roleplaying speaking back and forth on the command-line interface (CLI). Keep your messages concise and conversational. Vary the length of your messages frequently. Carefully plan your message to fit within the limits of the CLI. VARY YOUR MESSAGES, DO NOT REPEAT YOURSELF OFTEN.

        Your personality is: {personality}
        """
        prompt_template = self.simple_chat_prompt_template(system_prompt=system_prompt)
        model = self.llm_config.chat_model()
        chain = prompt_template | model
        return chain

    def simple_chat_loop(self):
        chat_history = ChatMessageHistory()
        chain = self.create_chat_chain()

        while True:
            message = input("User: ")
            chat_history.add_user_message(message)
            response = chain.invoke({"personality": self.identity.personality, "messages": chat_history.messages})
            chat_history.add_ai_message(response.content)
            print(f"{self.identity.name}: {response.content}")

import sys

config_file = sys.argv[1]

config = ConfigLoader(config_file=config_file).load_config()
env_file = config['env_file']

load_dotenv(dotenv_path=env_file)

cli_agent = SoftbeingBasicCLIAgent(config=config)
cli_agent.simple_chat_loop()
