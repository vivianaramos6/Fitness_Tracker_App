#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    def test_display_post_with_image(self):
        """Test that the display_post function correctly displays a post with an image."""
        # Create an AppTest instance for the display_post function
        at = AppTest.from_function(display_post)

        # Set the input arguments directly
        at.args = ("test_user", "https://example.com/profile.jpg", "2024-01-01 12:00:00", "This is a test post with an image.", "https://example.com/post_image.jpg")

        # Run the app
        at.run()

        # Get the rendered HTML
        rendered_html = at.get("markdown")[0].value

        # Expected HTML structure
        expected_html = """
        <div style="margin-bottom: 20px;">
            <img src="https://example.com/profile.jpg" width="50" style="border-radius: 50%;" />
            <strong>test_user</strong>
            <div style="font-size: 0.9em; color: gray;">2024-01-01 12:00:00</div>
            <p>This is a test post with an image.</p>
            <img src="https://example.com/post_image.jpg" style="max-width: 100%;" />
            <hr />
        </div>
        """

        # Normalize the HTML for comparison
        rendered_html = self._normalize_html(rendered_html)
        expected_html = self._normalize_html(expected_html)

        # Assert that the rendered HTML matches the expected HTML
        self.assertEqual(rendered_html, expected_html)

    def test_display_post_without_image(self):
        """Test that the display_post function correctly displays a post without an image."""
        # Create an AppTest instance for the display_post function
        at = AppTest.from_function(display_post)

        # Set the input arguments directly
        at.args = ("test_user", "https://example.com/profile.jpg", "2024-01-01 12:00:00", "This is a test post without an image.", None)

        # Run the app
        at.run()

        # Get the rendered HTML
        rendered_html = at.get("markdown")[0].value

        # Expected HTML structure
        expected_html = """
        <div style="margin-bottom: 20px;">
            <img src="https://example.com/profile.jpg" width="50" style="border-radius: 50%;" />
            <strong>test_user</strong>
            <div style="font-size: 0.9em; color: gray;">2024-01-01 12:00:00</div>
            <p>This is a test post without an image.</p>
            <hr />
        </div>
        """

        # Normalize the HTML for comparison
        rendered_html = self._normalize_html(rendered_html)
        expected_html = self._normalize_html(expected_html)

        # Assert that the rendered HTML matches the expected HTML
        self.assertEqual(rendered_html, expected_html)

    def test_display_post_with_empty_content(self):
        """Test that the display_post function handles empty content correctly."""
        # Create an AppTest instance for the display_post function
        at = AppTest.from_function(display_post)

        # Set the input arguments directly
        at.args = ("test_user", "https://example.com/profile.jpg", "2024-01-01 12:00:00", "", None)

        # Run the app
        at.run()

        # Get the rendered HTML
        rendered_html = at.get("markdown")[0].value

        # Expected HTML structure
        expected_html = """
        <div style="margin-bottom: 20px;">
            <img src="https://example.com/profile.jpg" width="50" style="border-radius: 50%;" />
            <strong>test_user</strong>
            <div style="font-size: 0.9em; color: gray;">2024-01-01 12:00:00</div>
            <p></p>
            <hr />
        </div>
        """

        # Normalize the HTML for comparison
        rendered_html = self._normalize_html(rendered_html)
        expected_html = self._normalize_html(expected_html)

        # Assert that the rendered HTML matches the expected HTML
        self.assertEqual(rendered_html, expected_html)

    def _normalize_html(self, html):
        """Normalize HTML for comparison by removing extra spaces and newlines."""
        return " ".join(html.split()).replace("> <", "><")


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_empty_workouts_list(self):
        at = AppTest.from_function(display_recent_workouts, args=([],))
        at.run()
        self.assertFalse(at.exception)
        at.header[0].value == 'Recent Workouts'
        at.markdown == ""

   


if __name__ == "__main__":
    unittest.main()
