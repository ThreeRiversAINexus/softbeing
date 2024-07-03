from softbeing.utils import TimeHelp, StringHelp, FileHelp, AsyncHelp
from softbeing.intentions.eleven_labs import SoftbeingElevenLabstool

from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import openai
import httpx
import re
import traceback
import discord

import logging
log = logging.getLogger(__name__)

class DiscordChatting():
    def __init__(self, body):
        self.body = body
        self.time = TimeHelp()
        self.string_help = StringHelp()
        self.file_help = FileHelp()

    async def discord_to_langchain_messages(self, discord_messages):
        ai_template = AIMessagePromptTemplate.from_template(template="{author}: {content}")
        human_template = HumanMessagePromptTemplate.from_template(template="{content}")
        langchain_messages = []
        chat_history = ""
        combined_content = ""  # To combine content of the same type
        last_author_type = None  # Track the last author type (AI or human)

        async for message in discord_messages:
            author = message.author
            content = message.clean_content.strip()
            # Skip if content is empty or all whitespace
            if not content:
                continue

            current_author_type = 'AI' if author == self.body.client.user else 'human'

            # If the current message type is different from the last, process the combined content
            if current_author_type != last_author_type and combined_content:
                if last_author_type == 'AI':
                    chat_message = ai_template.format(author=self.body.beliefs.personality.name, content=combined_content.strip())
                else:  # Human
                    chat_message = human_template.format(content=combined_content.strip())
                langchain_messages.append(chat_message)
                chat_history += combined_content + "\n"
                combined_content = ""  # Reset for the next group

            # Combine content, for human messages include the author's name for readability
            if current_author_type == 'human':
                combined_content += f"{author.display_name}: {content}\n"
            else:  # AI messages do not prepend the author's name
                combined_content += f"{content}\n"
            last_author_type = current_author_type

        # Handle the last combined content
        if combined_content:
            if last_author_type == 'AI':
                chat_message = ai_template.format(author=self.body.beliefs.personality.name, content=combined_content.strip())
            else:  # Human
                chat_message = human_template.format(content=combined_content.strip())
            langchain_messages.append(chat_message)
            chat_history += combined_content

        return chat_history, langchain_messages

    async def create_prompt_from_messages(self, discord_messages):
        # I need to do a better job of detecting
        # the pings and turning them into something readable to the bots.
        # I also need to do a better job of detecting when a message is referring to someone else (in a reply).
        prompt_messages = []
        
        discord_prompt_template = self.body.beliefs.personality.discord_prompt_template
        personality_prompt = self.body.beliefs.personality.personality

        discord_prompt_tokens = self.string_help.calculate_tokens(discord_prompt_template)
        log.info("Discord prompt length: " + str(discord_prompt_tokens))

        users_with_roles_list = self.body.beliefs.discord_knowledge.get_users_with_roles(discord_messages)

        users_with_roles = "\n".join(users_with_roles_list)
        system_message_template = SystemMessagePromptTemplate.from_template(
            template=discord_prompt_template,
        )
        chat_history = ""
        langchain_messages = []
        chat_history, langchain_messages = await self.discord_to_langchain_messages(AsyncHelp.async_generator_from_list(discord_messages))
        current_datetime = self.time.pretty_datetime()
        async with discord_messages[0].channel.typing():
             current_memory = await self.body.beliefs.discord_knowledge.generate_memory(langchain_messages, users_with_roles)
        personality_template = SystemMessagePromptTemplate.from_template(
            template=personality_prompt
        )
        bot_name = self.body.beliefs.personality.name
        personality = personality_template.format(
            bot_name=bot_name
        )
        personality = personality.content
        personality_tokens = self.string_help.calculate_tokens(personality)
        log.info("Personality length: " + str(personality_tokens))
        system_message = system_message_template.format(
            bot_name=bot_name,
            # Make this into a partial
            bot_personality=personality,
            users_with_roles=users_with_roles,
            current_datetime=current_datetime,
            current_memory=current_memory
        )
        log.info(system_message.content)
        log.info("System message length: " + str(self.string_help.calculate_tokens(system_message.content)))
        log.info("Chat history length: " + str(self.string_help.calculate_tokens(chat_history)))
        log.info(chat_history)

        prompt_messages += [system_message]
        # Get the last third of the langchain_messages
        # chat_history, langchain_messages = self.get_discord_message_context()
        langchain_messages = langchain_messages[-int(len(langchain_messages)-5):]
        prompt_messages.extend(langchain_messages)
        # prompt_messages += [special_system_message]

        prompt = ChatPromptTemplate.from_messages(prompt_messages)
        return prompt

    async def generate_message(self, prompt):
        model = ChatOpenAI(
            model=self.body.beliefs.llm_configuration.model_name,
            openai_api_key=self.body.beliefs.llm_configuration.api_key,
            openai_api_base=self.body.beliefs.llm_configuration.api_base,
            verbose=True,
            temperature=self.body.beliefs.llm_configuration.temperature,
            timeout=self.body.beliefs.llm_configuration.text_generation_timeout,
            max_tokens=self.body.beliefs.llm_configuration.max_tokens,
            frequency_penalty=self.body.beliefs.llm_configuration.frequency_penalty,
            presence_penalty=self.body.beliefs.llm_configuration.presence_penalty,
            streaming=True,
            stop=["<|end_of_text|>"],
            # model_kwargs={"stop": ["<|user|>"]}
        )

        output_parser = StrOutputParser()
        chain = prompt | model | output_parser
        log.info("Prompt length: " + str(self.string_help.calculate_tokens(prompt.format())))
        log.info(prompt.format())
        output = ""
        start_time = self.time.get_current_time()
        try:
            async for chunk in chain.astream({}):
                log.debug(chunk)
                output += chunk
        except openai.APITimeoutError:
            log.error("openai.APITimeoutError: Waiting too long.")
        except httpx.ReadTimeout:
            log.error("httpx.ReadTimeout: Waiting too long.")
        except Exception as e:
            log.error(f"Exception: {type(e)} - {type(e).__name__} - {e}")
        end_time = self.time.get_current_time()
        log.info("\n" + self.time.calculate_duration(start_time, end_time))

        output_tokens = self.string_help.calculate_tokens(output)
        log.info("Output length: " + str(output_tokens))
        # If the output begins with the name, remove it with regex
        # globally
        log.info("name: " + self.body.beliefs.personality.name)
        name = self.body.beliefs.personality.name
        if output.startswith(name):
            output = re.sub(f"\'?{name}\'?:", "", output)

        return output

    async def send_voice_message(self, channel, message):
        text2speech = SoftbeingElevenLabstool()
        # These are used by the bot for describing actions, its distracting.
        # Replace everything between two asterisks
        message = re.sub(r'\*.*?\*', '', message)
        # Remove all emojis
        message = await self.string_help.remove_emoji(message)

        # Return early if the message is empty or all whitespace
        voice = self.body.beliefs.personality.elevenlabs_voice
        if voice is not None and message.strip() != "":
            voice_message = text2speech.speak(message, voice)
            # Usually we ran out of 11labs api chars
            if voice_message is not None:
                voice_file = discord.File(voice_message)
                await channel.send(file=voice_file)

    async def invoke_chat_channel(self, prompt_task, channel):
        output = ""
        async with channel.typing():
            try:
                prompt = await prompt_task
                output = await self.generate_message(prompt)
                if (output and output != ""):
                    await channel.send(output)
            except Exception as e:
                traceback.print_exc()
        self.body.client.dispatch("sent_message", channel)
        if output and output != "":
            try:
                if self.body.beliefs.discord_configuration.enable_elevenlabs == 'True':
                    await self.send_voice_message(channel, output)
            except Exception as e:
                traceback.print_exc()
        
    async def invoke_chat_reply(self, prompt, message):
        async with message.channel.typing():
            output = await self.generate_message(prompt)
            if (output and output != ""):
                await message.reply(content=output)