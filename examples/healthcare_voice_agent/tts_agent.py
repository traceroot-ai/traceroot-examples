import os
import tempfile
from typing import Optional

import torch
from dotenv import load_dotenv
from TTS.api import TTS

load_dotenv()


class TTSAgent:
    """Text-to-Speech Agent for converting text responses to audio"""

    def __init__(self):
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize TTS with a good multilingual model
        # Using XTTS v2 which is great for voice cloning and multiple languages
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        except Exception:
            # Fallback to a simpler model if XTTS fails
            self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(self.device)

        # Store available speakers
        self.available_speakers = self.get_available_speakers()
        # Set default speaker if it's a multi-speaker model
        self.default_speaker = self.available_speakers[0] if self.available_speakers else None

    def synthesize_speech(
        self, 
        text: str, 
        output_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> dict[str, any]:
        """
        Convert text to speech and save as audio file
        
        Args:
            text: Text to convert to speech
            output_path: Path where to save the output audio file
            speaker_wav: Optional path to speaker voice for cloning
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dict containing success status and any error messages
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Normalize language code
            language = language.lower()
            if language == "english":
                language = "en"
            
            # Generate speech
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode
                try:
                    self.tts.tts_to_file(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language,
                        file_path=output_path
                    )
                except Exception as e:
                    # If voice cloning fails, fall back to default voice
                    print(f"Voice cloning failed, using default voice: {e}")
                    if self.default_speaker:
                        self.tts.tts_to_file(
                            text=text,
                            file_path=output_path,
                            speaker=self.default_speaker,
                            language=language
                        )
                    else:
                        self.tts.tts_to_file(text=text, file_path=output_path)
            else:
                # Default voice mode
                if self.default_speaker:
                    self.tts.tts_to_file(
                        text=text,
                        file_path=output_path,
                        speaker=self.default_speaker,
                        language=language
                    )
                else:
                    self.tts.tts_to_file(text=text, file_path=output_path)
            
            return {
                "success": True,
                "output_path": output_path,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error": f"TTS synthesis error: {str(e)}"
            }

    def synthesize_to_memory(
        self, 
        text: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> dict[str, any]:
        """
        Convert text to speech and return audio data in memory
        
        Args:
            text: Text to convert to speech
            speaker_wav: Optional path to speaker voice for cloning
            language: Language code
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            # Generate speech to memory
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode
                try:
                    wav_data = self.tts.tts(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language
                    )
                except Exception as e:
                    # If voice cloning fails, fall back to default voice
                    print(f"Voice cloning failed, using default voice: {e}")
                    wav_data = self.tts.tts(text=text)
            else:
                # Default voice mode
                wav_data = self.tts.tts(text=text)
            
            return {
                "success": True,
                "audio_data": wav_data,
                "sample_rate": 22050,  # Default sample rate for most TTS models
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "audio_data": None,
                "sample_rate": None,
                "error": f"TTS synthesis error: {str(e)}"
            }

    def get_available_speakers(self) -> list[str]:
        """
        Get list of available speakers for the loaded model
        
        Returns:
            List of speaker names/IDs
        """
        try:
            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                return self.tts.speakers
            else:
                return []
        except Exception:
            return []


def create_tts_agent():
    return TTSAgent() 