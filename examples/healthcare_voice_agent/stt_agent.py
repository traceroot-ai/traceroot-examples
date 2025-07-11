import os
import tempfile
from typing import Optional

import speech_recognition as sr
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()


class STTAgent:
    """Speech-to-Text Agent for converting audio to text"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise to improve recognition
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def transcribe_audio(self, audio_file_path: str) -> dict[str, str]:
        """
        Convert audio file to text using Whisper
        
        Args:
            audio_file_path: Path to the audio file (.mp3, .wav, etc.)
            
        Returns:
            Dict containing transcript and any error messages
        """
        try:
            # Convert audio to WAV format if needed
            wav_path = self._ensure_wav_format(audio_file_path)
            
            # Load audio file
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the audio
                audio_data = self.recognizer.record(source)
            
            # Use Whisper for transcription
            try:
                transcript = self.recognizer.recognize_whisper(
                    audio_data,
                    language="en"  # Use standard language code
                )
                
                # Clean up temporary file if we created one
                if wav_path != audio_file_path:
                    os.unlink(wav_path)
                
                return {
                    "success": True,
                    "transcript": transcript,
                    "language": "en",  # Return standard language code
                    "error": None
                }
                
            except sr.UnknownValueError:
                return {
                    "success": False,
                    "transcript": "",
                    "language": None,
                    "error": "Could not understand audio"
                }
            except sr.RequestError as e:
                return {
                    "success": False,
                    "transcript": "",
                    "language": None,
                    "error": f"Whisper error: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "transcript": "",
                "language": None,
                "error": f"Audio processing error: {str(e)}"
            }

    def _ensure_wav_format(self, audio_file_path: str) -> str:
        """
        Convert audio file to WAV format if needed
        
        Args:
            audio_file_path: Path to the input audio file
            
        Returns:
            Path to the WAV file (either original or converted)
        """
        if audio_file_path.lower().endswith('.wav'):
            return audio_file_path
        
        try:
            # Read the audio file
            data, samplerate = sf.read(audio_file_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav_path = temp_file.name
            
            # Write as WAV
            sf.write(wav_path, data, samplerate)
            
            return wav_path
            
        except Exception as e:
            raise Exception(f"Failed to convert audio to WAV format: {str(e)}")


def create_stt_agent():
    return STTAgent() 