# ScrumBot: Automated Scrum Transcription and Task Board Management

ScrumBot is a Python application that automates the process of updating a task board by listening to daily stand-up recordings. It uses open-source AI models to transcribe the audio, summarize key points, and update a JSON-based task board.

This tool is designed to be educational, modular, and run entirely on a local machine without relying on paid APIs.

## Features

- **Speech-to-Text**: Uses OpenAI's Whisper model for accurate transcription
- **Text Summarization**: Employs Hugging Face Transformers with BART model to extract tasks and blockers
- **Task Board Management**: Updates a JSON-based Kanban board with new tasks and blockers
- **Modular Design**: Well-organized codebase with separate modules for each functionality
- **Error Handling**: Comprehensive error handling for robust operation
- **Testing**: Unit tests for core functionality

## How It Works

1.  **Audio Input**: You provide an audio file (MP3 or WAV) of your team's daily stand-up meeting.
2.  **Transcription**: The application uses OpenAI's **Whisper** model to convert the speech in the audio file into text.
3.  **Summarization**: The transcript is then fed to a **BART** summarization model (from Hugging Face) to extract:
    *   Today's tasks for the team
    *   Any blockers or impediments
4.  **Task Board Update**: The application reads a local `board.json` file, which represents a simple Kanban-style board.
    *   New tasks are added to the "To Do" column.
    *   Blockers are added to the "Blockers" column.
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

Install dependencies using the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Usage

1.  Make sure you have an audio file (e.g., `scrum_meeting.mp3`) ready.
2.  Run the script from your terminal, passing the path to the audio file as an argument:

    ```bash
    python scrumbot_main.py /path/to/your/scrum_meeting.mp3
    ```

3.  To display the updated task board after processing:

    ```bash
    python scrumbot_main.py /path/to/your/scrum_meeting.mp3 --display-board
    ```

4.  To specify a custom task board file:

    ```bash
    python scrumbot_main.py /path/to/your/scrum_meeting.mp3 --board-file my_board.json
    ```

5.  After the script finishes, you can inspect the `board.json` file to see the updated tasks and blockers. The full transcript and summary will also be printed to the console.

## Running Tests

To run the unit tests:

```bash
python -m unittest discover tests
```

## Project Structure

```
├── scrumbot_main.py        # Main application entry point
├── requirements.txt        # Project dependencies
├── board.json             # Task board data (auto-generated)
├── scrumbot/              # Core modules
│   ├── __init__.py        # Package initializer
│   ├── transcription.py   # Audio transcription functionality
│   ├── summarization.py   # Text summarization functionality
│   └── task_board.py      # Task board management
└── tests/                 # Unit tests
    └── test_task_board.py # Tests for task board functionality
```

