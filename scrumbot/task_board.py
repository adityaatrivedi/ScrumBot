"""
Task board management module for ScrumBot.
Handles reading from and writing to the JSON task board.
"""

import json
import os
import re


def parse_tasks_from_summary(summary_text):
    """
    Parses tasks from the summary text.
    
    Args:
        summary_text (str): The summary text from the summarization model.
        
    Returns:
        list: A list of parsed tasks.
    """
    if not summary_text or not summary_text.strip():
        return []
    
    # Split by common sentence separators but filter out empty strings
    potential_tasks = [task.strip() for task in re.split(r'[.!?]+', summary_text) if task.strip()]
    
    # Filter out any remaining prompt fragments or very short strings
    tasks = [task for task in potential_tasks if len(task) > 20 and "summary" not in task.lower() and "extract" not in task.lower()]
    
    return tasks


def parse_blockers_from_summary(summary_text):
    """
    Parses blockers from the summary text.
    
    Args:
        summary_text (str): The summary text from the summarization model.
        
    Returns:
        list: A list of parsed blockers.
    """
    if not summary_text or not summary_text.strip():
        return []
    
    # Split by common sentence separators but filter out empty strings
    potential_blockers = [blocker.strip() for blocker in re.split(r'[.!?]+', summary_text) if blocker.strip()]
    
    # Filter out any remaining prompt fragments or very short strings
    blockers = [blocker for blocker in potential_blockers if len(blocker) > 20 and "summary" not in blocker.lower() and "extract" not in blocker.lower()]
    
    return blockers


def categorize_items(transcript, tasks, blockers):
    """
    Categorizes items based on keywords in the original transcript.
    
    Args:
        transcript (str): The original transcript.
        tasks (list): List of potential tasks.
        blockers (list): List of potential blockers.
        
    Returns:
        tuple: (categorized_tasks, categorized_blockers, done_items)
    """
    categorized_tasks = []
    categorized_blockers = []
    done_items = []
    
    # Combine all items for processing
    all_items = list(set(tasks + blockers))  # Remove duplicates
    
    # Keywords for categorization
    blocker_keywords = ["blocker", "bug", "issue", "problem", "impediment", "urgent", "stuck", "delay"]
    done_keywords = ["finished", "completed", "done", "finished", "completed"]
    task_keywords = ["task", "assign", "schedule", "implement", "develop", "create", "update", "fix", "work on"]
    
    for item in all_items:
        item_lower = item.lower()
        
        # Check if it's a blocker
        if any(keyword in item_lower for keyword in blocker_keywords):
            categorized_blockers.append(item)
        # Check if it's done
        elif any(keyword in item_lower for keyword in done_keywords):
            done_items.append(item)
        # Check if it's a task
        elif any(keyword in item_lower for keyword in task_keywords):
            categorized_tasks.append(item)
        # Default to task if none of the above
        else:
            categorized_tasks.append(item)
    
    return categorized_tasks, categorized_blockers, done_items


def update_task_board(summaries, transcript="", board_file="board.json"):
    """
    Updates the task board JSON file based on the generated summaries.
    
    Args:
        summaries (dict): The dictionary of summaries from the summarization function.
        transcript (str): The original transcript for better categorization.
        board_file (str): The path to the JSON file representing the task board.
    """
    print(f"Updating the task board at {board_file}...")
    try:
        # Check if the board file exists; if not, create a default structure.
        if not os.path.exists(board_file):
            board = {"To Do": [], "In Progress": [], "Done": [], "Blockers": []}
        else:
            # Open the JSON file and load its contents into a Python dictionary.
            with open(board_file, 'r') as f:
                board = json.load(f)

        # Validate summaries format
        if not isinstance(summaries, dict) or 'today' not in summaries or 'blockers' not in summaries:
            raise ValueError("Invalid summaries format. Expected dict with 'today' and 'blockers' keys.")

        # Parse tasks and blockers from summaries
        new_tasks = parse_tasks_from_summary(summaries['today'])
        new_blockers = parse_blockers_from_summary(summaries['blockers'])
        
        # Categorize items based on the original transcript
        if transcript:
            categorized_tasks, categorized_blockers, done_items = categorize_items(transcript, new_tasks, new_blockers)
        else:
            # Fallback to simple categorization
            categorized_tasks = new_tasks
            categorized_blockers = new_blockers
            done_items = []
        
        # Add new tasks to the "To Do" list.
        for task in categorized_tasks:
            # Check if task already exists in any column
            task_exists = False
            for column in board.values():
                if task in column:
                    task_exists = True
                    break
            
            if not task_exists:
                board["To Do"].append(task)
                print(f"  - Added task to 'To Do': {task}")

        # Add new blockers to the "Blockers" list.
        for blocker in categorized_blockers:
            if blocker not in board["Blockers"]:
                board["Blockers"].append(blocker)
                print(f"  - Added blocker: {blocker}")
                
        # Add done items to the "Done" list.
        for item in done_items:
            if item not in board["Done"]:
                board["Done"].append(item)
                print(f"  - Added to 'Done': {item}")
                
        # Write the updated dictionary back to the JSON file.
        # `indent=4` makes the JSON file human-readable.
        with open(board_file, 'w') as f:
            json.dump(board, f, indent=4)
            
        print("Task board updated successfully.")
        return board
    except Exception as e:
        print(f"Error updating task board: {e}")
        raise


def load_task_board(board_file="board.json"):
    """
    Loads the current task board from the JSON file.
    
    Args:
        board_file (str): The path to the JSON file representing the task board.
        
    Returns:
        dict: The task board data.
    """
    if not os.path.exists(board_file):
        return {"To Do": [], "In Progress": [], "Done": [], "Blockers": []}
    
    with open(board_file, 'r') as f:
        return json.load(f)


def display_task_board(board_file="board.json"):
    """
    Displays the current task board in a formatted way.
    
    Args:
        board_file (str): The path to the JSON file representing the task board.
    """
    board = load_task_board(board_file)
    
    print("\n--- Current Task Board ---")
    for section, items in board.items():
        print(f"\n{section}:")
        if items:
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item}")
        else:
            print("  (No items)")
