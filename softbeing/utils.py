import datetime
import logging

class TimeHelp():
    def get_current_time(self):
        import time
        """Returns the current time in seconds since the Epoch."""
        return time.time()
    
    def minutes_ago(self, minutes):
        """Returns the time threshold in seconds for a given number of minutes."""
        time_threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return time_threshold

    def calculate_duration(self, start_time, end_time):
        """Calculates the duration between two time points in minutes and seconds.
        Args:
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
        Returns:
            tuple: A tuple containing the duration in minutes and seconds.
        """
        duration_seconds = end_time - start_time
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        return f"Process took: {int(minutes)} minutes, {int(seconds)} seconds"

    def pretty_datetime(self):
        import pytz
        current_datetime = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%B %d, %Y %I:%M:%S %p")
        return current_datetime

    def file_postfix(self):
        return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

class StringHelp():
    async def remove_emoji(self, message):
        import emoji # version 2.0+
        # https://carpedm20.github.io/emoji/docs/#migrating-to-version-2-0-0
        message = emoji.replace_emoji(message, replace='')
        return message

    def calculate_tokens(self, text):
        import tiktoken
        model_name = 'gpt-4'
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens

class FileHelp():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def slurp_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
    def slurp_json(self, file_path):
        import json
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")

class AsyncHelp():
    @staticmethod
    async def async_generator_from_list(lst):
        for item in lst:
            yield item

class LangchainHelp():
    @staticmethod
    async def serialize_messages(messages):
        """
        Convert a list of langchain HumanMessage objects into a JSON serializable format.
        """
        import pprint
        from softbeing.utils import AsyncHelp
        log = logging.getLogger(__name__)
        serialized_messages = []
        log.debug(pprint.pformat(messages[0].__dict__))
        async for message in AsyncHelp.async_generator_from_list(messages):
            serialized_message = {
                'type': message.type,  # Assuming author is already a simple string
                'content': message.content
            }
            serialized_messages.append(serialized_message)
        return serialized_messages
    