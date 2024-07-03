from softbeing.intentions.discord_chatting import DiscordChatting
from softbeing.utils import TimeHelp, LangchainHelp, AsyncHelp

from discord.ext import commands
import discord
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
        discord_messages = await self.body.beliefs.discord_knowledge.get_discord_message_context(ctx.message)
        raw_history, last_messages = await self.intend_to_chat.discord_to_langchain_messages(AsyncHelp.async_generator_from_list(discord_messages))

        from pprint import pprint
        pprint(last_messages)
        pprint(discord_messages)

        serialized_messages = await LangchainHelp.serialize_messages(last_messages)

        prompt_template = await self.intend_to_chat.create_prompt_from_messages(discord_messages)
        system_prompt = prompt_template.format()

        filename = f"{name}-{now}.json"
        data_to_save = {
            'metadata': {
                'author': name,
                'timestamp': now
            },
            'data': {
                'messages': serialized_messages,
                'system_prompt': system_prompt
            }
        }
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
        channel_name = "unknown"
        if isinstance(channel, discord.DMChannel):
            channel_name = channel.id
        
        if isinstance(channel, discord.TextChannel):
            channel_name = channel.name

        log.info(f"Activity noticed in {channel_name}")

        # Improved logic would go here
        if self.notice_cooldown > 0:
            log.info(f"Notice cooldown: {self.notice_cooldown}")
            self.notice_cooldown -= 1
            return

        log.info(f"Notice activity in {channel_name}")
        first_message = messages[-1]
        context_messages = await self.body.beliefs.discord_knowledge.get_discord_message_context(first_message)
        log.debug("A")
        prompt_task = asyncio.create_task(self.intend_to_chat.create_prompt_from_messages(context_messages))
        log.debug("B")
        asyncio.create_task(self.intend_to_chat.invoke_chat_channel(prompt_task, channel))
        log.debug("C")
        self.body.client.dispatch("waiting_to_generate", channel)
        log.debug("D")

        self.notice_cooldown = self.body.beliefs.discord_configuration.notice_cooldown

def load_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data_loaded = json.load(file)
    return data_loaded['data'], data_loaded['metadata']