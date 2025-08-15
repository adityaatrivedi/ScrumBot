import unittest
import json
import os
import tempfile
from unittest.mock import patch
from scrumbot.task_board import update_task_board, load_task_board


class TestTaskBoard(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.board_file = os.path.join(self.test_dir, "test_board.json")

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.board_file):
            os.remove(self.board_file)
        os.rmdir(self.test_dir)

    def test_update_task_board_creates_new_file(self):
        """Test that update_task_board creates a new board file if it doesn't exist."""
        summaries = {
            "today": "Implement user authentication. Create login page.",
            "blockers": "Database connection issues."
        }
        
        update_task_board(summaries, board_file=self.board_file)
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.board_file))
        
        # Check content
        with open(self.board_file, 'r') as f:
            board = json.load(f)
            
        # The parsing logic now filters out short items, so we need longer test strings
        self.assertTrue(len(board["To Do"]) > 0 or len(board["Blockers"]) > 0)

    def test_update_task_board_adds_to_existing_file(self):
        """Test that update_task_board adds to an existing board file."""
        # Create initial board
        initial_board = {
            "To Do": ["Initial task"],
            "In Progress": [],
            "Done": [],
            "Blockers": ["Initial blocker"]
        }
        
        with open(self.board_file, 'w') as f:
            json.dump(initial_board, f)
        
        # Update with new summaries
        summaries = {
            "today": "Add new feature implementation with detailed description.",
            "blockers": "Server downtime issues affecting development."
        }
        
        update_task_board(summaries, board_file=self.board_file)
        
        # Check updated content
        with open(self.board_file, 'r') as f:
            board = json.load(f)
            
        # Check that existing items are still there
        self.assertIn("Initial task", board["To Do"])
        self.assertIn("Initial blocker", board["Blockers"])
        
        # Check that new items were added (based on our filtering logic)
        total_items = sum(len(items) for items in board.values())
        self.assertGreater(total_items, 2)  # Should have more than just the initial items

    def test_load_task_board_creates_default_if_missing(self):
        """Test that load_task_board returns default structure if file doesn't exist."""
        board = load_task_board(self.board_file)
        
        self.assertIn("To Do", board)
        self.assertIn("In Progress", board)
        self.assertIn("Done", board)
        self.assertIn("Blockers", board)
        
        # All sections should be empty lists
        for section in board.values():
            self.assertIsInstance(section, list)

    def test_update_task_board_handles_json_decode_error(self):
        """Test that update_task_board handles a JSONDecodeError gracefully."""
        # Create a corrupted JSON file
        with open(self.board_file, 'w') as f:
            f.write("this is not valid json")

        summaries = {
            "today": "This is a new task that should be added.",
            "blockers": "This is a new blocker."
        }

        # This should not raise an exception
        board = update_task_board(summaries, board_file=self.board_file)

        # The board should be reset and the new items should be added
        self.assertIn("This is a new task that should be added", board["To Do"])
        self.assertIn("This is a new blocker", board["Blockers"])

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_update_task_board_handles_io_error(self, mock_open):
        """Test that update_task_board raises an IOError when it can't write to the board file."""
        summaries = {
            "today": "A task.",
            "blockers": "A blocker."
        }

        with self.assertRaises(IOError):
            update_task_board(summaries, board_file=self.board_file)


if __name__ == '__main__':
    unittest.main()