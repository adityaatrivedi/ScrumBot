"""
Task board management module for ScrumBot.
Handles reading from and writing to the JSON task board.
"""

import json
import os
import re
from scrumbot.config import TODO_COLUMN, IN_PROGRESS_COLUMN, DONE_COLUMN, BLOCKERS_COLUMN


def parse_items_from_summary(summary_text):
    """
    Parses items from the summary text.
    
    Args:
        summary_text (str): The summary text from the summarization model.
        
    Returns:
        list: A list of parsed items.
    """
    if not summary_text or not summary_text.strip():
        return []
    
    # Split by common sentence separators but filter out empty strings
    potential_items = [item.strip() for item in re.split(r'[.!?]+', summary_text) if item.strip()]
    
    # Filter out any remaining prompt fragments or very short strings
    items = [item for item in potential_items if len(item) > 20 and "summary" not in item.lower() and "extract" not in item.lower()]
    
    return items


def deduplicate_items(items):
    """
    Removes duplicate items from a list, considering similarity.
    
    Args:
        items (list): List of items to deduplicate.
        
    Returns:
        list: Deduplicated list of items.
    """
    if not items:
        return []
    
    # Simple deduplication based on substring matching
    unique_items = []
    for item in items:
        # Check if this item is a substring of any existing item or vice versa
        is_duplicate = False
        for existing_item in unique_items:
            # If one is a substring of the other, consider it a duplicate
            if item in existing_item or existing_item in item:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_items.append(item)
    
    return unique_items


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
    
    # Combine all items for processing and deduplicate
    all_items = deduplicate_items(list(set(tasks + blockers)))  # Remove exact duplicates first
    
    # Keywords for categorization
    blocker_keywords = ["blocker", "bug", "issue", "problem", "impediment", "urgent", "stuck", "delay", "api.*bug", "not started"]
    done_keywords = ["finished", "completed", "done", "finished", "completed", "mark that as done"]
    task_keywords = ["task", "assign", "schedule", "implement", "develop", "create", "update", "fix", "work on", "to do"]
    
    for item in all_items:
        item_lower = item.lower()
        
        # Check if it's a blocker
        if any(re.search(keyword, item_lower) for keyword in blocker_keywords):
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
    
    # Deduplicate each category
    categorized_tasks = deduplicate_items(categorized_tasks)
    categorized_blockers = deduplicate_items(categorized_blockers)
    done_items = deduplicate_items(done_items)
    
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
            board = {TODO_COLUMN: [], IN_PROGRESS_COLUMN: [], DONE_COLUMN: [], BLOCKERS_COLUMN: []}
        else:
            try:
                # Open the JSON file and load its contents into a Python dictionary.
                with open(board_file, 'r') as f:
                    board = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading or parsing board file: {e}")
                # If the file is corrupted or can't be read, start with a fresh board
                board = {TODO_COLUMN: [], IN_PROGRESS_COLUMN: [], DONE_COLUMN: [], BLOCKERS_COLUMN: []}

        # Validate summaries format
        if not isinstance(summaries, dict) or 'today' not in summaries or 'blockers' not in summaries:
            raise ValueError("Invalid summaries format. Expected dict with 'today' and 'blockers' keys.")

        # Parse tasks and blockers from summaries
        new_tasks = parse_items_from_summary(summaries['today'])
        new_blockers = parse_items_from_summary(summaries['blockers'])
        
        # Categorize items based on the original transcript
        if transcript:
            categorized_tasks, categorized_blockers, done_items = categorize_items(transcript, new_tasks, new_blockers)
        else:
            # Fallback to simple categorization with deduplication
            categorized_tasks = deduplicate_items(new_tasks)
            categorized_blockers = deduplicate_items(new_blockers)
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
                board[TODO_COLUMN].append(task)
                print(f"  - Added task to '{TODO_COLUMN}': {task}")

        # Add new blockers to the "Blockers" list.
        for blocker in categorized_blockers:
            if blocker not in board[BLOCKERS_COLUMN]:
                board[BLOCKERS_COLUMN].append(blocker)
                print(f"  - Added blocker: {blocker}")
                
        # Add done items to the "Done" list.
        for item in done_items:
            if item not in board[DONE_COLUMN]:
                board[DONE_COLUMN].append(item)
                print(f"  - Added to 'Done': {item}")
                
        # Write the updated dictionary back to the JSON file.
        try:
            with open(board_file, 'w') as f:
                json.dump(board, f, indent=4)
        except IOError as e:
            print(f"Error writing to board file: {e}")
            raise
            
        print("Task board updated successfully.")
        return board
    except ValueError as e:
        print(f"Error updating task board: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during task board update: {e}")
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
        return {TODO_COLUMN: [], IN_PROGRESS_COLUMN: [], DONE_COLUMN: [], BLOCKERS_COLUMN: []}
    
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
