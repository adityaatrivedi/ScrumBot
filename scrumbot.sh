#!/bin/bash
# scrumbot.sh - Simple launcher script for ScrumBot

# Check if audio file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <audio_file> [--display-board] [--board-file <file>]"
    echo "Example: $0 meeting.mp3 --display-board"
    exit 1
fi

# Run the ScrumBot application
python3 scrumbot_main.py "$@"