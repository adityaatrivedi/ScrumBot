# ScrumBot: Automated Scrum Transcription and Task Board Management

ScrumBot is a Python script that automates the process of updating a task board by listening to daily stand-up recordings. It uses open-source AI models to transcribe the audio, summarize key points, and update a JSON-based task board.

This tool is designed to be simple, educational, and run entirely on a local machine without relying on paid APIs.

## How It Works

1.  **Audio Input**: You provide an audio file (MP3 or WAV) of your team's daily stand-up meeting.
2.  **Transcription**: The script uses OpenAI's **Whisper** model to convert the speech in the audio file into text.
3.  **Summarization**: The transcript is then fed to a **BART** summarization model (from Hugging Face) to extract three key pieces of information:
    *   What each person accomplished yesterday.
    *   What they plan to do today.
    *   Any blockers they are facing.
4.  **Task Board Update**: The script reads a local `board.json` file, which represents a simple Kanban-style board.
    *   New tasks from the "today" summary are added to the "To Do" column.
    *   Blockers are added to the "Blockers" column.
    *   (Note: Moving tasks to "Done" is a complex NLP problem; this version focuses on adding new tasks and blockers).
5.  **Save**: The updated task board is saved back to `board.json`.

## Setup and Installation

This project requires Python 3.8+ and the `ffmpeg` system utility.

**1. Install ffmpeg**

`ffmpeg` is a required dependency for Whisper to process audio files.

*   **On macOS (using Homebrew):**
    ```bash
    brew install ffmpeg
    ```
*   **On Windows (using Chocolatey):**
    ```bash
    choco install ffmpeg
    ```
*   **On Linux (using apt):**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

**2. Create a Virtual Environment (Recommended)**

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

**3. Install Python Dependencies**

The core AI and audio processing libraries are installed via pip. Note that `torch` is a large library and may take some time to download.

```bash
pip install transformers torch
pip install openai-whisper
pip install soundfile librosa
```

## Usage

1.  Make sure you have an audio file (e.g., `scrum_meeting.mp3`) ready.
2.  Run the script from your terminal, passing the path to the audio file as an argument:

    ```bash
    python scrumbot.py /path/to/your/scrum_meeting.mp3
    ```

3.  After the script finishes, you can inspect the `board.json` file to see the updated tasks and blockers. The full transcript and summary will also be printed to the console.

