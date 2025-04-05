#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
import streamlit as st
import pytest
import streamlit as st
from io import StringIO
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

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
    """Tests the display_activity_summary function.
       These tests were generated and refined by Gemini
       https://gemini.google.com/app/e59ba99961bd1367"""

    def test_no_workout_data(self):
        """
        Test that the function displays the correct message when no workout data is available.
        """
        at = AppTest.from_function(display_activity_summary, args=([],))
        at.run()
        self.assertEqual(at.markdown[0].value, "No workout data available.")

    def test_workout_data_display(self):

        '''Test that the function correctly displays the workout summaries and past workouts table.'''
        
        workouts_list = [
            {
                'workout_id': 'workout1',
                'start_timestamp': '2024-01-01 00:00:00',
                'end_timestamp': '2024-01-01 00:30:00',
                'start_lat_lng': (1.23, 4.56),
                'end_lat_lng': (7.89, 0.12),
                'distance': 5.0,
                'steps': 10000,
                'calories_burned': 250
            },
            {
                'workout_id': 'workout2',
                'start_timestamp': '2024-01-02 00:00:00',
                'end_timestamp': '2024-01-02 00:30:00',
                'start_lat_lng': (3.45, 6.78),
                'end_lat_lng': (9.01, 2.34),
                'distance': 8.0,
                'steps': 15000,
                'calories_burned': 400
            }
        ]

        at = AppTest.from_function(display_activity_summary, args=(workouts_list,))
        at.run()

        self.assertIn("Workout 1 Summary", at.markdown[2].value)
        self.assertIn("*Steps*<br>10000", at.markdown[3].value)
        self.assertIn("Workout 2 Summary", at.markdown[10].value)
        self.assertIn("*Steps*<br>15000", at.markdown[11].value)
        
class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    # Test the session state messages being updated
    def test_session_state_messages(self):
        # Initialize session state for messages
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []

        user_input = "I need advice"
        st.session_state['messages'].append(f"You: {user_input}")
    
        # Simulate bot's response
        st.session_state['messages'].append("Bot: Here's your advice!")

        # Check that the message was added to the session state
        assert "You: I need advice" in st.session_state['messages']
        assert "Bot: Here's your advice!" in st.session_state['messages']


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
