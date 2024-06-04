import os
import discord

class DiscordConfiguration():
    # history_window_minutes=20
    history_window_minutes=10
    history_window_limit=20
    notice_cooldown_variance=2 # NOT IMPLEMENTED YET, INTENDED TO RANDOMIZE THE RESPONSES TIMING
    notice_cooldown=0
    notice_interval=1
    enable_elevenlabs=False
    command_prefix='$'
    notice_roles = ['']
    
    def get_token(self):
        return os.environ.get('DISCORD_BOT_TOKEN')

    def __init__(self, config):
        self.log_filename = config['log_filename']
        self.history_window_minutes = config['history_window_minutes']
        self.history_window_limit = config['history_window_limit']
        self.notice_cooldown_variance = config['notice_cooldown_variance']
        self.notice_cooldown = config['notice_cooldown']
        self.notice_interval = config['notice_interval']
        self.enable_elevenlabs = config['enable_elevenlabs']
        self.command_prefix = config['command_prefix']
        self.notice_roles = config['notice_roles']
        self.focus_roles = config['focus_roles']
        # config['monitored_guilds'] is a hash
        # the keys are the guild names
        # the values are a list of channel names
        self.monitored_guilds = config['monitored_guilds']
        # self.monitored_channels = config['monitored_guilds']

    def get_intents(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.presences = True
        intents.members = True
        return intents