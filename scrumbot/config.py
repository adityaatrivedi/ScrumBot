"""
Configuration for ScrumBot.
"""

# Summarization models
DEFAULT_MODEL = "facebook/bart-large-cnn"
FALLBACK_MODELS = [
    "google-t5/t5-small",
    "google/pegasus-xsum"
]

# Task board columns
TODO_COLUMN = "To Do"
IN_PROGRESS_COLUMN = "In Progress"
DONE_COLUMN = "Done"
BLOCKERS_COLUMN = "Blockers"
