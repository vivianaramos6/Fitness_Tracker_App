#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st


# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Displays a single user post with the provided details.

    Args:
        username (str): The username of the poster.
        user_image (str): URL or path to the user's profile image.
        timestamp (str): The timestamp of the post.
        content (str): The text content of the post.
        post_image (str): URL or path to the image attached to the post.
    """
    import streamlit as st
    # Render the post as HTML using st.markdown
    html = f"""
    <div style="margin-bottom: 20px;">
        <img src="{user_image}" width="50" style="border-radius: 50%;" />
        <strong>{username}</strong>
        <div style="font-size: 0.9em; color: gray;">{timestamp}</div>
        <p>{content}</p>
        {f'<img src="{post_image}" style="max-width: 100%;" />' if post_image else ''}
        <hr />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
        

def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
