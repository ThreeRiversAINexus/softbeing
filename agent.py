import discord
from discord.ext import commands
import os
import json
import asyncio
from dotenv import load_dotenv
import logging
import traceback
import sys

from discord.ext import commands
from softbeing.beliefs import Beliefs, DiscordKnowledge, DiscordConfiguration, PersonalityConfiguration, LLMConfiguration
from softbeing.desires import ChattingCog, MonitoringCog, Desires

def build_file_logger(logging_name):
    LOG_DIR = os.environ.get('LOG_DIR', "/logs")
    # Add LOG_DIR to logging_name
    logging_path = os.path.join(LOG_DIR, logging_name)
    file_handler = logging.FileHandler(filename=logging_path, encoding='utf-8', mode='a')
    return file_handler 

stdout_logger = logging.StreamHandler(stream=sys.stdout)
file_logger = build_file_logger('softbeing_agent.log')
logging.basicConfig(handlers=[file_logger, stdout_logger], level=logging.INFO)
log = logging.getLogger(__name__)
class SoftbeingAgent():
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()
        self.locks = {}
        # noticing_lock isnt used anywhere actually yet
        # it was an experiment with synchronizing
        # the monitoring and chatting
        self.locks['noticing_lock'] = asyncio.Lock()
        self.locks['saving_lock'] = asyncio.Lock()
    
    def setup_beliefs(self, configuration):
        self.beliefs = Beliefs()
        self.beliefs.env_file = configuration['env_file']

        if configuration['discord_configuration']:
            self.beliefs.llm_configuration = LLMConfiguration(config=configuration['llm_configuration'])
            self.beliefs.discord_configuration = DiscordConfiguration(config=configuration['discord_configuration'])
            self.beliefs.discord_knowledge = DiscordKnowledge(config=self.beliefs.discord_configuration, llm=self.beliefs.llm_configuration)

        if configuration['personality_configuration']:
            self.beliefs.personality = PersonalityConfiguration(config=configuration['personality_configuration'])
    
    def setup_desires(self):
        self.desires = Desires()
        self.desires.chatting_cog = ChattingCog(self)
        self.desires.monitoring_cog = MonitoringCog(self)

    def create_discord_client(self):
        intents = self.beliefs.discord_configuration.get_intents()
        client = commands.Bot(command_prefix=self.beliefs.discord_configuration.command_prefix, intents=intents)

        log.info("Creating discord client")

        # This is the optimal place to load your cogs up
        @client.event
        async def setup_hook():
            log.info("Running setup_hook")
            self.setup_desires()

            await self.client.add_cog(self.desires.chatting_cog)
            await self.client.add_cog(self.desires.monitoring_cog)

        self.client = client
        return self.client

    def build_logger(self):
        logging_name = self.beliefs.discord_configuration.log_filename
        return build_file_logger(logging_name)

    def run_discord_client(self):
        token = self.beliefs.discord_configuration.get_token()
        handler = self.build_logger()
        while True:
            try:
                log.info("Running client")
                self.client.run(token, log_handler=handler, log_level=logging.INFO)
            except discord.errors.ConnectionClosed as e:
                log.info(f"ConnectionClosed: {e}")
            except Exception as e:
                log.info(f"Exception: {e}")
                traceback.print_exc()
                break

    def load_config(self):
        # Actually need to go through and redo the beliefs
        with open(self.config_file) as f:
            configuration = json.load(f)
        self.setup_beliefs(configuration)

# get the json in the file 'softbeing_config.json'
import sys
def setup(config_file):
    softbeing = SoftbeingAgent(config_file)
    softbeing.create_discord_client()
    softbeing.run_discord_client()
config_file = sys.argv[1]
with open(config_file) as f:
    configuration = json.load(f)
env_file = configuration['env_file']
load_dotenv(dotenv_path=env_file)

setup(config_file)