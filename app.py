#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts, users

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    # st.title('Welcome to SDS!')

    # # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

    tabs = st.tabs(["Home", "Activity Summary", "Recent Workouts", "GenAI Advice"])

    # Display the selected page based on the active tab
    with tabs[0]:
        display_home_page()
    with tabs[1]:
        display_activity_summary_page()
    with tabs[2]:
        display_recent_workouts_page()
    with tabs[3]:
        display_genai_advice_page()


def display_home_page():
    """Displays the home page with user posts."""
    st.title('User Posts')

    user_profile = get_user_profile(userId)
    user_posts = get_user_posts(userId)

    # Set a valid placeholder image URL for post_image
    placeholder_post_image = 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'

    for post in user_posts:
        user_id = post.get('user_id', 'Unknown User')
        username = users.get(user_id, {}).get('username', 'Unknown User')
 
        display_post(
            username=username,  # Use the fetched username
            user_image=user_profile['profile_image'],  # Use the profile image from user profile
            timestamp=post.get('timestamp', ''),
            content=post.get('content', ''),
            post_image=placeholder_post_image  # Use the placeholder image URL
        )

def display_activity_summary_page():
    """Displays the activity summary page."""
    st.title('Activity Summary')
    # Placeholder
    

def display_recent_workouts_page():
    """Displays the recent workouts page."""
    st.title('Recent Workouts')
    # Placeholder

def display_genai_advice_page():
    """Displays the GenAI advice page."""
    st.title('GenAI Advice')
    # Placeholder



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
