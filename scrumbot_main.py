"""
ScrumBot: Automated Scrum Transcription and Task Board Management

This script automates the process of updating a task board by listening to daily 
stand-up recordings. It uses open-source AI models to transcribe the audio, 
summarize key points, and update a JSON-based task board.
"""

import argparse
import sys
import os

# Add the scrumbot package to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from scrumbot.transcription import transcribe_audio
from scrumbot.summarization import summarize_transcript
from scrumbot.task_board import update_task_board, display_task_board


def main():
    """
    The main function that orchestrates the entire process.
    """
    try:
        # argparse is the standard Python library for creating command-line interfaces.
        # We define one required argument: the path to the audio file.
        parser = argparse.ArgumentParser(description="Transcribe a scrum meeting and update a task board.")
        parser.add_argument("audio_file", help="The path to the audio file (e.g., mp3, wav).")
        parser.add_argument("--board-file", default="board.json", help="Path to the task board JSON file.")
        parser.add_argument("--display-board", action="store_true", help="Display the current task board after update.")
        parser.add_argument("--model", choices=["bart", "pegasus", "xsum"], default="bart", 
                          help="Summarization model to use (default: bart)")
        args = parser.parse_args()

        # --- Execute the workflow ---
        # 1. Transcribe the audio to get the text.
        transcript = transcribe_audio(args.audio_file)
        print("\n--- Transcript ---")
        print(transcript)
        
        # 2. Summarize the transcript to get actionable items.
        model_map = {
            "bart": "facebook/bart-large-cnn",
            "pegasus": "google/pegasus-xsum",
            "xsum": "facebook/bart-large-xsum"
        }
        model_name = model_map.get(args.model, "facebook/bart-large-cnn")
        print(f"\n--- Using {args.model.upper()} model for summarization ---")
        summaries = summarize_transcript(transcript, model_name=model_name)
            
        print("\n--- Summary ---")
        print(f"Today's Tasks: {summaries['today']}")
        print(f"Blockers: {summaries['blockers']}")
        
        # 3. Update the JSON task board with the new information.
        print("\n--- Board Updates ---")
        update_task_board(summaries, transcript, args.board_file)
        
        # 4. Optionally display the updated board
        if args.display_board:
            display_task_board(args.board_file)
            
    except FileNotFoundError as e:
        print(f"File error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


# This standard Python construct ensures that the `main()` function is called
# only when the script is run directly (not when it's imported as a module).
if __name__ == "__main__":
    main()