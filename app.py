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
from goals_page import show_goals_page

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    tabs = st.tabs(["My Posts", "Community", "Activity", "Fitness Groups", "Goals"])

    if 'current_group' not in st.session_state:
        st.session_state.current_group = None
    if 'show_goals' not in st.session_state:
        st.session_state.show_goals = False

    # Display the selected page based on the active tab
    with tabs[0]:
        display_user_posts(userId)
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
    with tabs[4]:  # Goals tab
        show_goals_page(userId)

# def display_user_posts():
#     """Displays the home page with user posts."""
#     st.title('User Posts')

#     user_profile = get_user_profile(userId)
#     user_posts = get_user_posts(userId)

#     posts = get_user_posts('user1')
#     for post in posts:
#         display_post(
#             username=post['username'],
#             user_image=post['user_image'],
#             timestamp=post['timestamp'],
#             content=post['content'],
#             post_image=post['image']
#         )


def display_user_posts(user_id):
    """Displays the home page with user posts."""
    st.title('Your Activity Feed')
    
    # User profile section
    with st.container():
        user_profile = get_user_profile(user_id)
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(user_profile['profile_image'], width=80)  # Removed extra quote
        with col2:
            st.subheader(user_profile['full_name'])
            st.caption(f"@{user_profile['username']}")
    
    # User posts section
    st.divider()
    user_posts = get_user_posts(user_id)
    
    if not user_posts:
        st.info("No posts yet. Share your fitness journey!")
    else:
        for post in user_posts:
            display_post(
                username=post['username'],
                user_image=post['user_image'],
                timestamp=post['timestamp'],
                content=post['content'],
                post_image=post['image']
            )

if __name__ == '__main__':
    st.set_page_config(
        page_title="Fitness Community App",
        page_icon="🏋️",
        layout="wide"
    )
    display_app_page()
