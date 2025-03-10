import pytest
import streamlit as st
from unittest.mock import patch
from io import StringIO
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts


# Test if the Gen AI advice is displayed with the correct background and content
def test_display_genai_advice():
    content = "Set a small goal, like 5 minutes of movement."
    timestamp = "2025-03-09 10:00"

    # Capture the output of the streamlit app
    with patch("sys.stdout", new_callable=StringIO) as fake_out:
        display_genai_advice(timestamp, content)
        output = fake_out.getvalue()

    # Check that the content is rendered correctly in the output
    assert "Set a small goal, like 5 minutes of movement." in output

    # Check that the background color (mauve) is in the output
    assert "background-color: #E0B0FF" in output

    # Optional: Check for image rendering if you mock the image path
    # assert 'assets/images/motivation.jpeg' in output  # Check if image path is correctly rendered


# Test if the button click functionality works as expected
@patch("streamlit.button", return_value=True)  # Mocking the button press
def test_button_click(mock_button):
    with patch("streamlit.write") as mock_write:
        # Test the "Previous Advice" button
        assert st.button("Previous Advice") == True
        mock_write.assert_called_with("Click to access previous advice")

        # Test the "New Advice" button
        assert st.button("New Advice") == True
        mock_write.assert_called_with("click to generate new advice")


# Test user input and Gen AI advice triggering
@patch("streamlit.text_input", return_value="I need advice")  # Mocking user input
def test_user_input_for_advice(mock_input):
    # Simulate user input
    user_input = st.text_input("You: ", "")
    assert user_input == "I need advice"
    
    # Simulate the response and check if the message was added to session state
    if "advice" in user_input.lower():
        # Mock session state and display Gen AI advice
        st.session_state['messages'] = ["You: I need advice"]
        
        # Here we would capture the output
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            display_genai_advice(
                "2025-03-09 10:00",
                "Set a small goal, like 5 minutes of movement. Once you start, you'll likely keep going! 'Discipline is choosing between what you want now and what you want most.'",
                "assets/images/motivation.jpeg"
            )
            output = fake_out.getvalue()
        
        # Assert the response was correctly rendered
        assert "Set a small goal, like 5 minutes of movement." in output


# Test the session state messages being updated
def test_session_state_messages():
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
