from langchain_community.tools.eleven_labs.text2speech import _import_elevenlabs
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_community.tools import ElevenLabsText2SpeechTool

from typing import Optional

import tempfile
import traceback
import logging
log = logging.getLogger(__name__)

class SoftbeingElevenLabstool(ElevenLabsText2SpeechTool):
    def speak(
        self, query: str, voice: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        log.info("Inside SoftbeingElevenLabsTool")
        elevenlabs = _import_elevenlabs()
        try:
            speech = elevenlabs.generate(text=query, model=self.model, voice=voice, output_format="mp3_44100_128")
            if speech is not None:
                with tempfile.NamedTemporaryFile(
                    mode="bx", suffix=".mp3", delete=False
                ) as f:
                    f.write(speech)
                return f.name
        except elevenlabs.api.error.RateLimitError as e:
            log.error(f"RateLimitError: {e}")
        except Exception as e:
            traceback.print_exc()