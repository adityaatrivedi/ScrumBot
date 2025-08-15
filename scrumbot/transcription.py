"""
Transcription module for ScrumBot.
Handles audio transcription using OpenAI's Whisper model.
"""

import whisper
import os


def transcribe_audio(audio_path):
    """
    Transcribes an audio file using the Whisper ASR model.
    
    Args:
        audio_path (str): The file path to the audio file (MP3, WAV, etc.).
        
    Returns:
        str: The transcribed text from the audio.
    """
    # Check if audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print("Loading Whisper model and transcribing audio... (This may take a moment)")
    try:
        # Load the base English model. For other languages, you could change this.
        model = whisper.load_model("base.en") 
        # The transcribe function takes the file path and runs the model.
        result = model.transcribe(audio_path)
        print("Transcription complete.")
        return result['text']
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise