import json
import argparse
import whisper
from transformers import pipeline
import os
import ssl
import certifi

# --- SSL Certificate Fix for macOS ---
# This addresses a common issue on macOS where Python's default SSL certificates
# are not found, leading to 'CERTIFICATE_VERIFY_FAILED' errors when downloading
# models. This code block configures Python's SSL context to use the certificate
# bundle provided by the 'certifi' library, which is a standard and trusted
# source for SSL certificates.
try:
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except Exception as e:
    print(f"Warning: Could not apply SSL certificate fix: {e}")
    pass

# --- 1. Transcription using Whisper ---
# This section defines a function to convert the audio file into text.
# Whisper is an open-source model from OpenAI that is highly accurate.
# We use the "base" model here because it offers a good balance of speed and accuracy
# for running on a local machine without a powerful GPU.
def transcribe_audio(audio_path):
    """
    Transcribes an audio file using the Whisper ASR model.
    
    Args:
        audio_path (str): The file path to the audio file (MP3, WAV, etc.).
        
    Returns:
        str: The transcribed text from the audio.
    """
    print("Loading Whisper model and transcribing audio... (This may take a moment)")
    # Load the base English model. For other languages, you could change this.
    model = whisper.load_model("base.en") 
    # The transcribe function takes the file path and runs the model.
    result = model.transcribe(audio_path)
    print("Transcription complete.")
    return result['text']

# --- 2. Summarization using Hugging Face Transformers ---
# This section uses a pre-trained model from Hugging Face to summarize the transcript.
# We use the BART (Bidirectional and Auto-Regressive Transformer) model, which is
# excellent for summarization tasks. The "pipeline" function from the transformers
# library makes it incredibly easy to use these complex models.
def summarize_transcript(transcript):
    """
    Summarizes the transcript to extract tasks and blockers using a Hugging Face model.
    
    Args:
        transcript (str): The text transcript from the Whisper model.
        
    Returns:
        dict: A dictionary containing summaries for tasks to do and blockers.
    """
    print("Loading summarization model and generating summary...")
    # Initialize the summarization pipeline with the BART model.
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # We create specific prompts to guide the model. This helps it focus on
    # the exact information we need to extract from the meeting.
    prompt_todo = f"Summarize the tasks that the team will work on today based on the following text:\n\n{transcript}"
    prompt_blockers = f"Summarize any blockers, impediments, or problems mentioned in the following text:\n\n{transcript}"
    
    # The summarizer is run on each prompt. We set a min and max length
    # to control the output size and prevent it from being too verbose or too brief.
    summary_todo = summarizer(prompt_todo, max_length=150, min_length=20, do_sample=False)
    summary_blockers = summarizer(prompt_blockers, max_length=100, min_length=10, do_sample=False)
    
    print("Summarization complete.")
    return {
        "today": summary_todo[0]['summary_text'],
        "blockers": summary_blockers[0]['summary_text']
    }

# --- 3. Task Board Management ---
# This section handles the logic for reading and writing to our "task board,"
# which is stored in a simple JSON file.
def update_task_board(summaries, board_file="board.json"):
    """
    Updates the task board JSON file based on the generated summaries.
    
    Args:
        summaries (dict): The dictionary of summaries from the summarization function.
        board_file (str): The path to the JSON file representing the task board.
    """
    print(f"Updating the task board at {board_file}...")
    # Check if the board file exists; if not, create a default structure.
    if not os.path.exists(board_file):
        board = {"To Do": [], "In Progress": [], "Done": [], "Blockers": []}
    else:
        # Open the JSON file and load its contents into a Python dictionary.
        with open(board_file, 'r') as f:
            board = json.load(f)

    # --- Task Parsing Logic ---
    # This is a simple parsing strategy. We assume the summary lists tasks
    # separated by sentences or newlines. A more advanced solution might use
    # more sophisticated NLP to parse these tasks more reliably.
    
    # Add new tasks to the "To Do" list.
    # We split the summary by periods to get individual sentences/tasks.
    new_tasks = [task.strip() for task in summaries['today'].split('.') if task.strip()]
    for task in new_tasks:
        if task not in board["To Do"] and task not in board["In Progress"]:
            board["To Do"].append(task)
            print(f"  - Added task to 'To Do': {task}")

    # Add new blockers to the "Blockers" list.
    new_blockers = [blocker.strip() for blocker in summaries['blockers'].split('.') if blocker.strip()]
    for blocker in new_blockers:
        if blocker not in board["Blockers"]:
            board["Blockers"].append(blocker)
            print(f"  - Added blocker: {blocker}")
            
    # Write the updated dictionary back to the JSON file.
    # `indent=4` makes the JSON file human-readable.
    with open(board_file, 'w') as f:
        json.dump(board, f, indent=4)
        
    print("Task board updated successfully.")

# --- Main Execution ---
# This is the entry point of our script. It's wrapped in a `main` function
# and called when the script is executed from the command line.
def main():
    """
    The main function that orchestrates the entire process.
    """
    # argparse is the standard Python library for creating command-line interfaces.
    # We define one required argument: the path to the audio file.
    parser = argparse.ArgumentParser(description="Transcribe a scrum meeting and update a task board.")
    parser.add_argument("audio_file", help="The path to the audio file (e.g., mp3, wav).")
    args = parser.parse_args()

    # --- Execute the workflow ---
    # 1. Transcribe the audio to get the text.
    transcript = transcribe_audio(args.audio_file)
    print("\n--- Transcript ---")
    print(transcript)
    
    # 2. Summarize the transcript to get actionable items.
    summaries = summarize_transcript(transcript)
    print("\n--- Summary ---")
    print(f"Today's Tasks: {summaries['today']}")
    print(f"Blockers: {summaries['blockers']}")
    
    # 3. Update the JSON task board with the new information.
    print("\n--- Board Updates ---")
    update_task_board(summaries)

# This standard Python construct ensures that the `main()` function is called
# only when the script is run directly (not when it's imported as a module).
if __name__ == "__main__":
    main()
