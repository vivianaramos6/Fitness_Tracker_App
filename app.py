#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_post
from data_fetcher import get_user_posts, get_user_profile
from community_page import show_community_page
from activity_page import activity_page
from fitness_groups import display_fitness_groups, display_group_page

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    tabs = st.tabs(["My Posts", "Community", "Activity", "Fitness Groups"])

    if 'current_group' not in st.session_state:
        st.session_state.current_group = None

    # Display the selected page based on the active tab
    with tabs[0]:
        display_user_posts()
    with tabs[1]:
        show_community_page(userId)
    with tabs[2]:
        activity_page(userId)
    with tabs[3]:
        if st.session_state.current_group:
            display_group_page(st.session_state.current_group, userId)
            if st.button("← Back to Groups Hub"):
                st.session_state.current_group = None
                st.rerun()
        else:
            display_fitness_groups(userId)

def display_user_posts():
    """Displays the home page with user posts."""
    st.title('User Posts')

    user_profile = get_user_profile(userId)
    user_posts = get_user_posts(userId)

    posts = get_user_posts('user1')
    for post in posts:
        display_post(
            username=post['username'],
            user_image=post['user_image'],
            timestamp=post['timestamp'],
            content=post['content'],
            post_image=post['image']
        )

if __name__ == '__main__':
    display_app_page()
