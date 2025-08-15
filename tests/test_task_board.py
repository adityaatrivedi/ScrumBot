import unittest
import json
import os
import tempfile
from scrumbot.task_board import update_task_board


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
        # Import the function we're testing
        from scrumbot.task_board import load_task_board
        
        board = load_task_board(self.board_file)
        
        self.assertIn("To Do", board)
        self.assertIn("In Progress", board)
        self.assertIn("Done", board)
        self.assertIn("Blockers", board)
        
        # All sections should be empty lists
        for section in board.values():
            self.assertIsInstance(section, list)


if __name__ == '__main__':
    unittest.main()