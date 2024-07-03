from softbeing.utils import TimeHelp

from discord.ext import commands, tasks
import discord

import asyncio
import logging
log = logging.getLogger(__name__)

# Not sure how to make this load from config file
NOTICE_INTERVAL=1

class MonitoringCog(commands.Cog):
    def __init__(self, body):
        self.body = body 
        NOTICE_INTERVAL = self.body.beliefs.discord_configuration.notice_interval
        self.time = TimeHelp()
        self.check_messages.start()
        self.locks = {}
        log.info("MonitoringCog")
    
    @commands.command()
    async def notice(self, ctx):
        # This is where we'll implement invoking chat directly
        # especially useful in DMs
        self.body.client.dispatch("notice_activity", ctx.message.channel, [ctx.message])

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f'Logged in as {self.body.client.user.name}')

    def cog_unload(self):
        self.check_messages.stop()  # Cancel the task when the cog is unloaded

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            log.info("DM received")
        else:
            return

    async def decide_to_chat(self, messages):
        # Immediately return False if messages list is empty
        if not messages:
            log.info("No messages to decide on.")
            return False

        # If the last message was from ourselves then do not send another message.
        message_count = len(messages)
        log.info(f"Message count: {message_count}")
        if message_count <= 0:
            return False
        last_author = messages[-1].author
        log.info(f"last_author: {last_author.name} content: {messages[-1].content}")
        if last_author == self.body.client.user:
            return False
        return True

    @tasks.loop(minutes=NOTICE_INTERVAL)
    async def check_messages(self):
        knowledge = self.body.beliefs.discord_knowledge
        config = self.body.beliefs.discord_configuration
        history_window = config.history_window_minutes
        guild_list = await knowledge.list_guilds(self.body.client)
        # print(guild_list)
        log.info("Checking messages...")
        monitored_guilds = config.monitored_guilds.keys()

        for guild_name in guild_list:
            if guild_name not in monitored_guilds:
                continue
            # print(guild_name)
            guild = await knowledge.get_guild_by_name(self.body.client, guild_name)
            channels = guild.channels
            monitored_channels = [channel for channel in channels if channel.name in config.monitored_guilds[guild_name]]
            # print(monitored_channels)
            for channel in monitored_channels:
                if self.locks.get(guild_name, {}).get(channel.name, 0) == 1:
                    continue
                time_threshold = self.time.minutes_ago(history_window)
                messages_with_notice_role = 0
                messages = []
                async for message in channel.history(after=time_threshold, limit=20, oldest_first=True):
                    # print("Inside channel.history")
                    member = message.author
                    # print(f"{message.author.display_name} {message.content}")
                    messages += [message]
                    if isinstance(member, discord.Member):
                        roles = [role.name for role in member.roles]
                        if config.notice_roles in roles:
                            messages_with_notice_role += 1

                if messages_with_notice_role == 0:
                    # await channel.send("CHAT REVIVE!")
                    self.body.client.dispatch("dead_chat", channel)
                    continue

                decision_to_chat = await self.decide_to_chat(messages)
                if messages_with_notice_role > 0 and decision_to_chat:
                    log.info("Dispatching activity")
                    self.body.client.dispatch("notice_activity", channel, messages)
                    # await channel.send(response)

    @commands.Cog.listener()
    async def on_waiting_to_generate(self, channel):
        log.info("waiting_to_generate")
        if isinstance(channel, discord.TextChannel):
            self.locks.setdefault(channel.guild.name, {})
            self.locks[channel.guild.name][channel.name] = 1
        # elif isinstance(channel, discord.DMChannel):
        #     self.locks["DM"][channel.recipient.name] = 1
        # Add a lock for just the channel
        # self.check_messages.cancel()

    @commands.Cog.listener()
    async def on_sent_message(self, channel):
        await asyncio.sleep(60)
        log.info("sent_message")
        if isinstance(channel, discord.TextChannel):
            self.locks.setdefault(channel.guild.name, {})
            self.locks[channel.guild.name][channel.name] = 0

        # Release the lock on the channel
        # self.check_messages.start()

    @check_messages.before_loop
    async def before_check_messages(self):
        await self.body.client.wait_until_ready()  # Wait until the bot logs in