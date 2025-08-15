"""
Summarization module for ScrumBot.
Handles text summarization using Hugging Face Transformers.
"""

from transformers import pipeline
import os

from scrumbot.config import DEFAULT_MODEL, FALLBACK_MODELS

def _summarize_with_model(transcript, model_name):
    """
    Internal function to summarize text with a specific model.
    """
    summarizer = pipeline("summarization", model=model_name)
    
    max_input_length = 1024
    truncated_transcript = transcript[:max_input_length]
    
    summary_todo = summarizer(
        truncated_transcript, 
        max_length=130, 
        min_length=30, 
        do_sample=False,
        truncation=True
    )
    
    summary_blockers = summarizer(
        truncated_transcript, 
        max_length=80, 
        min_length=15, 
        do_sample=False,
        truncation=True
    )
    
    return {
        "today": summary_todo[0]['summary_text'],
        "blockers": summary_blockers[0]['summary_text']
    }

def summarize_transcript(transcript, model_name=DEFAULT_MODEL):
    """
    Summarizes the transcript to extract tasks and blockers using a Hugging Face model.
    
    Args:
        transcript (str): The text transcript from the Whisper model.
        model_name (str): The name of the Hugging Face model to use for summarization.
        
    Returns:
        dict: A dictionary containing summaries for tasks to do and blockers.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty or None")
    
    models_to_try = [model_name] + [model for model in FALLBACK_MODELS if model != model_name]
    
    for model in models_to_try:
        try:
            print(f"Loading summarization model {model} and generating summary...")
            return _summarize_with_model(transcript, model)
        except Exception as e:
            print(f"Error during summarization with {model}: {e}")
            continue
            
    print("All models failed. Returning original transcript.")
    return {
        "today": transcript,
        "blockers": transcript
    }


