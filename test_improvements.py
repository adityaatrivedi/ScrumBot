#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from scrumbot.summarization import summarize_transcript
from scrumbot.task_board import update_task_board, display_task_board, deduplicate_items

# Test deduplication function
def test_deduplication():
    print("Testing deduplication function...")
    items = [
        "I need to fix the bug in the payments API",
        "Pre-I need to fix the bug in the payments API",
        "Fix the payments API bug",
        "Update login page design",
        "Work on login page design"
    ]
    
    deduplicated = deduplicate_items(items)
    print(f"Original items: {len(items)}")
    for item in items:
        print(f"  - {item}")
    
    print(f"\nDeduplicated items: {len(deduplicated)}")
    for item in deduplicated:
        print(f"  - {item}")

# Test model selection
def test_model_selection():
    print("\n" + "="*50)
    print("Testing different models...")
    
    # Sample transcript
    transcript = "Here's the update of the today's standard. First, assign John the task of updating the login page design. It should be completed by Friday and is currently in progress. Next, Pre-I need to fix the bug in the payments API. It is a blocker and should be marked as urgent and not started yet. Also, I finished the documentation for the onboarding process. So, mark that as done. Lastly, add a task to schedule a client call on Tuesday. Assign it to me and mark it as to do. That's all."
    
    models = [
        "facebook/bart-large-cnn",
        "google/pegasus-xsum"
    ]
    
    for model in models:
        print(f"\n--- Testing {model} ---")
        try:
            summaries = summarize_transcript(transcript, model)
            print(f"Tasks summary: {summaries['today']}")
            print(f"Blockers summary: {summaries['blockers']}")
        except Exception as e:
            print(f"Error with {model}: {e}")

if __name__ == "__main__":
    test_deduplication()
    test_model_selection()