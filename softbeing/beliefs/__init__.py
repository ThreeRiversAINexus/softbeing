from .discord_configuration import DiscordConfiguration
from .discord_knowledge import DiscordKnowledge
from .personality_configuration import PersonalityConfiguration
from .llm import LLMConfiguration

class Beliefs():
    discord_knowledge = None
    discord_configuration = None
    llm_configuration = None
    personality = None
    env_file = None