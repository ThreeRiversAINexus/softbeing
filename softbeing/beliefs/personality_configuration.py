from softbeing.utils import FileHelp
class PersonalityConfiguration():
    def __init__(self, config):
        file_help = FileHelp()
        self.name = config['name']
        self.personality = file_help.slurp_file(config['personality_file'])
        self.elevenlabs_voice = config['elevenlabs_voice']
        self.discord_prompt_template = file_help.slurp_file(config['discord_prompt_template_file'])