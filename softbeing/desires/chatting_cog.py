from softbeing.intentions.discord_chatting import DiscordChatting
from softbeing.utils import TimeHelp, LangchainHelp

from discord.ext import commands
import asyncio
import logging
import json 

log = logging.getLogger(__name__)

class ChattingCog(commands.Cog):
    def __init__(self, body):
        self.body = body
        self.time = TimeHelp()
        self.notice_cooldown = self.body.beliefs.discord_configuration.notice_cooldown
        self.current_input = ""
        self.current_memory = ""
        self.intend_to_chat = DiscordChatting(body)

    @commands.command()
    async def save(self, ctx):
        name = self.body.beliefs.personality.name
        now = self.time.file_postfix()
        raw_history, last_messages = await self.intend_to_chat.discord_to_langchain_messages(ctx.channel.history(limit=200))

        serialized_messages = await LangchainHelp.serialize_messages(last_messages)

        filename = f"{name}-{now}.json"
        data_to_save = {
            'metadata': {
                'author': name,
                'timestamp': now
            },
            'data': serialized_messages
        }
        async with self.body.locks['saving_lock']:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data_to_save, file, ensure_ascii=False, indent=4)

    @commands.command()
    async def reload(self, ctx):
        # Reload the config and
        # .env file
        self.body.load_config()

    @commands.Cog.listener()
    async def on_dead_chat(self, channel):
        log.info(f"Dead chat noticed in {channel.name}")

    @commands.Cog.listener()
    async def on_notice_activity(self, channel, messages):
        log.info(f"Activity noticed in {channel.name}")

        # Improved logic would go here
        if self.notice_cooldown > 0:
            log.info(f"Notice cooldown: {self.notice_cooldown}")
            self.notice_cooldown -= 1
            return

        log.info(f"Notice activity in {channel.name}")
        first_message = messages[-1]
        context_messages = await self.body.beliefs.discord_knowledge.get_discord_message_context(first_message)
        log.debug("A")
        prompt_task = asyncio.create_task(self.intend_to_chat.create_prompt_from_messages(context_messages))
        log.debug("B")
        asyncio.create_task(self.intend_to_chat.invoke_chat_channel(prompt_task, channel))
        log.debug("C")
        self.body.client.dispatch("waiting_to_generate")
        log.debug("D")

        self.notice_cooldown = self.body.beliefs.discord_configuration.notice_cooldown

def load_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data_loaded = json.load(file)
    return data_loaded['data'], data_loaded['metadata']