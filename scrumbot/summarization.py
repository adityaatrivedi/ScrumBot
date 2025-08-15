"""
Summarization module for ScrumBot.
Handles text summarization using Hugging Face Transformers.
"""

from transformers import pipeline


def summarize_transcript(transcript):
    """
    Summarizes the transcript to extract tasks and blockers using a Hugging Face model.
    
    Args:
        transcript (str): The text transcript from the Whisper model.
        
    Returns:
        dict: A dictionary containing summaries for tasks to do and blockers.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty or None")
    
    print("Loading summarization model and generating summary...")
    try:
        # Initialize the summarization pipeline with the BART model.
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Truncate the transcript to a reasonable length to avoid warnings
        max_input_length = 1024
        truncated_transcript = transcript[:max_input_length]
        
        # For extraction tasks, we'll use the summarizer on the actual content
        # but with parameters that encourage extraction over summarization
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
        
        print("Summarization complete.")
        return {
            "today": summary_todo[0]['summary_text'],
            "blockers": summary_blockers[0]['summary_text']
        }
    except Exception as e:
        print(f"Error during summarization: {e}")
        # Fallback approach: try a different method
        try:
            # Try with a different model that might work better for extraction
            summarizer = pipeline("summarization", model="google-t5/t5-small")
            
            # Truncate the transcript
            max_input_length = 512
            truncated_transcript = transcript[:max_input_length]
            
            summary_todo = summarizer(
                f"standup tasks: {truncated_transcript}",
                max_length=100,
                min_length=20,
                do_sample=False,
                truncation=True
            )
            
            summary_blockers = summarizer(
                f"standup blockers: {truncated_transcript}",
                max_length=60,
                min_length=10,
                do_sample=False,
                truncation=True
            )
            
            return {
                "today": summary_todo[0]['summary_text'],
                "blockers": summary_blockers[0]['summary_text']
            }
        except Exception as e2:
            print(f"Fallback summarization also failed: {e2}")
            # Last resort: return a simplified parsing of the original transcript
            return {
                "today": transcript,
                "blockers": transcript
            }