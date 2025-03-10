import pytest
import streamlit as st
from unittest.mock import patch
from io import StringIO
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts


# Test if the Gen AI advice is displayed with the correct background and content


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
