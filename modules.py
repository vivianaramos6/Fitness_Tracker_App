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
    """Displays a 'recent workouts' component that showcases a user's recent workout history.

    workouts_list: A list of dictionaries where each dictionary contains:
        - start_timestamp: The start time of the workout in '%Y-%m-%d %H:%M:%S' format
        - end_timestamp: The end time of the workout in '%Y-%m-%d %H:%M:%S' format
        - duration: The total time spent during the workout (e.g., '45 min')
        - distance: The distance covered during the workout (e.g., '3.5 miles')
        - steps: The number of steps taken during the workout (e.g., '7,200 steps')
        - calories: The number of calories burned during the workout (e.g., '4,500 kcal')
        - start_location: The GPS coordinates or address where the workout started
        - stop_location: The GPS coordinates or address where the workout ended

    This component renders each workout as a card with a summary of the workout's 
    details. It also displays an 'Add Workout' button in the form of a card that 
    allows users to add new workout data.
    """
    import streamlit as st
    from datetime import datetime

    st.header("Recent Workouts")
    if not workouts_list:
        st.write("No recent workouts available.")
        return

    for workout in workouts_list:
        # Calculate the duration of the workout
        start_time = datetime.strptime(workout['start_timestamp'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(workout['end_timestamp'], '%Y-%m-%d %H:%M:%S')
        duration = end_time - start_time
        workout['duration'] = str(duration)  # Store the duration in the 'duration' key

    # Create a 3-column grid layout
    cols = st.columns(3)
    for i, workout in enumerate(workouts_list):
        with cols[i % 3]:
            # Add a blue border for the selected workout (you can change this condition)
            if i == len(workouts_list) - 1:  
                st.markdown(
                    f"""
                    <div style="border: 2px solid #0066ff; border-radius: 10px; padding: 15px;">
                        <h5><b>DATE/TIME</b></h5>
                        <p><b>DURATION:</b> {workout['duration']}</p>
                        <p><b>DISTANCE:</b> {workout['distance']}</p>
                        <p><b>STEPS:</b> {workout['steps']}</p>
                        <p><b>CALORIES:</b> {workout['calories_burned']}</p>
                        <p><b>START:</b> {workout['start_lat_lng']}</p>
                        <p><b>STOP:</b> {workout['end_lat_lng']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                # Normal card for other workouts
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px;">
                        <h5><b>DATE/TIME</b></h5>
                        <p><b>DURATION:</b> {workout['duration']}</p>
                        <p><b>DISTANCE:</b> {workout['distance']}</p>
                        <p><b>STEPS:</b> {workout['steps']}</p>
                        <p><b>CALORIES:</b> {workout['calories_burned']}</p>
                        <p><b>START:</b> {workout['start_lat_lng']}</p>
                        <p><b>STOP:</b> {workout['end_lat_lng']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    # Add the "+" card to add a new workout
    with cols[len(workouts_list) % 3]:
        st.markdown(
            """
            <div style="border: 1px dashed #ccc; border-radius: 10px; padding: 15px; text-align: center; cursor: pointer;">
                <h1>+</h1>
                <p>Add Workout</p>
            </div>
            """, 
            unsafe_allow_html=True
        )



def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
