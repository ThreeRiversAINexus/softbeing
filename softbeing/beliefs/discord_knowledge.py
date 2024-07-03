from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
import logging
import discord

log = logging.getLogger(__name__)

class DiscordKnowledge():
    def __init__(self, config=None, llm=None):
        if config is None:
            raise ValueError("config cannot be None")
        if llm is None:
            raise ValueError("llm cannot be None")
        self.configuration = config
        # The values in self.llm are LLMConfiguration, not an actual LLM
        self.llm = llm

    async def get_discord_message_context(self, message, limit=None):
        log.info("get_discord_message_context")
        if limit is None:
            limit = self.configuration.history_window_limit
        history_window = self.configuration.history_window_minutes
        channel = message.channel
        messages = [message]
        log.info("Getting history")
        async for that_message in channel.history(before=message, limit=limit, oldest_first=False):
            if that_message.clean_content != "":
                messages += [that_message]
            if that_message == message:
                continue
        messages.reverse()
        log.info("get_discord_message_context")
        for message in messages:
            log.info(f"{message.author.display_name}: {message.clean_content}")
        return messages

    async def generate_memory(self, langchain_messages, users_with_roles):
        llm = OpenAI(
            temperature=0.5,
            model=self.llm.model_name,
            openai_api_key=self.llm.api_key,
            openai_api_base=self.llm.api_base,
            frequency_penalty=self.llm.frequency_penalty,
            presence_penalty=self.llm.presence_penalty,
            model_kwargs={"stop": ["<|end_of_text|>"]}
        )
        summarization_template = PromptTemplate.from_template("""
##### Discord Users (Roles) #####
{users_with_roles}
##### Discord Chat Log #####
{chat_history}
##### ASSISTANT INSTRUCTIONS #####
YOU ARE THE SUMMARIZATION AI. Generate a very long summary of the discord chat log. 
##### Summary #####
        """)
        chain = summarization_template | llm | StrOutputParser()
        chat_history = ""
        summary = ""
        for msg in langchain_messages:
            chat_history += f"{msg.content}\n"
        try:
            summary = await chain.ainvoke({"chat_history": chat_history,
                                    "users_with_roles": users_with_roles})
        # generic exception handler that dispatches sent_activity
        except Exception as e:
            log.error(f"Exception: {type(e)} - {type(e).__name__} - {e}")
        
        # memory.save_context({"input": "hi"}, {"output": "whats up"})
        # memory.save_context({"input": "not much you"}, {"output": "not much"})
        return summary

    def get_users_with_roles(self, messages):
        authors_roles = {}

        focus_roles = self.configuration.focus_roles

        for message in messages:
            author = message.author
            if isinstance(author, discord.Member):
                # Collect role names for members, excluding '@everyone' and focusing on focus_roles if specified
                role_names = {role.name for role in author.roles if role.name != "@everyone" and (not focus_roles or role.name in focus_roles)}
            elif isinstance(author, discord.User):
                # Users outside of guild context don't have roles
                role_names = {"No roles - User not in server"}
            else:
                role_names = {"Unknown"}

            # Use author's ID as a unique identifier to avoid duplicate authors
            if author.id not in authors_roles:
                authors_roles[author.id] = {"name": author.display_name, "roles": role_names}
            else:
                # Update the roles if the author is already in the dictionary
                authors_roles[author.id]["roles"].update(role_names)

        # Format the authors and their roles into a list of strings
        output_lines = [f"{author_info['name']} ({', '.join(roles)})" for author_info in authors_roles.values() for roles in [author_info["roles"]]]

        return output_lines

    async def list_guilds(self, member):
        """Returns a list of guilds the bot is part of."""
        return [guild.name for guild in member.guilds]

    async def get_guild_by_name(self, member, guild_name):
        """Returns the first guild with the given name, or None if not found."""
        for guild in member.guilds:
            if guild.name == guild_name:
                return guild
        return None
