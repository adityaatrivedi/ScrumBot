
import unittest
from unittest.mock import patch, MagicMock
from scrumbot.summarization import summarize_transcript

class TestSummarization(unittest.TestCase):

    @patch('scrumbot.summarization.pipeline')
    def test_summarize_transcript_success(self, mock_pipeline):
        """Test successful summarization with the default model."""
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = [{'summary_text': 'This is a summary.'}]
        mock_pipeline.return_value = mock_summarizer

        transcript = "This is a long transcript to be summarized."
        result = summarize_transcript(transcript)

        self.assertEqual(result['today'], 'This is a summary.')
        self.assertEqual(result['blockers'], 'This is a summary.')
        mock_pipeline.assert_called_with("summarization", model="facebook/bart-large-cnn")

    @patch('scrumbot.summarization.pipeline')
    def test_summarize_transcript_fallback(self, mock_pipeline):
        """Test the fallback mechanism when the primary model fails."""
        # Simulate failure for the first model, success for the second
        mock_pipeline.side_effect = [
            Exception("Model not found"),
            MagicMock(return_value=[{'summary_text': 'Fallback summary.'}])
        ]

        transcript = "This is another long transcript."
        result = summarize_transcript(transcript, model_name="facebook/bart-large-cnn")

        self.assertEqual(result['today'], 'Fallback summary.')
        self.assertEqual(result['blockers'], 'Fallback summary.')
        self.assertEqual(mock_pipeline.call_count, 2)

    def test_summarize_transcript_empty_input(self):
        """Test that an empty transcript raises a ValueError."""
        with self.assertRaises(ValueError):
            summarize_transcript("")

    

if __name__ == '__main__':
    unittest.main()
