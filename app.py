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
        st.title("Gen Ai Advice")
        #smaller left hand side and the larger right hand side. If the left hand side is less than 2, it would squish the words
        col1, col2 = st.columns([2, 4])  

        #Left hand side shows the previous advice and new chat (this isnt implemented yet)
        with col1:
            st.header("Advice")
            if st.button("Previous Advice"):
                st.write("Click to acess previous advice")
            if st.button("New Advice"):
                st.write("click to generate new advice")

        with col2:
            advice_container = st.container()  
            if 'messages' not in st.session_state:
                st.session_state['messages'] = []
            #labels the user and user input varibale
            user_input = st.text_input("You: ", "")

            if user_input:
                st.session_state.messages.append(f"You: {user_input}")
                
                #displaying the advice at the top after the user enters that they need fitness advvice
                if "advice" in user_input.lower():
                    #used gen ai to get information from datafetcher
                    advice_data = get_genai_advice(user_id=1)  # Assuming user_id = 1 for now

                    timestamp = advice_data['timestamp']
                    content = advice_data['content']
                    image = 'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
                    with advice_container: 
                        display_genai_advice(timestamp,content, image)
                


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
    workouts_list = get_user_workouts(userId)
    display_recent_workouts(workouts_list)

def display_genai_advice(timestamp, content, image=None):
    st.header("Gen Ai Advice")
    st.subheader(f"Timestamp: {timestamp}")
    #st.write(content)
    #Making the content a mauve color background to match the website theme. Used gen ai to create this code for the color
    #cant use write content because content variable is already used in the markdown
    st.markdown(f"""
        <div style='background-color: #E0B0FF; padding: 10px; border-radius: 15px; margin: 10px 0;'>
            <p style='color: white;'>{content}</p>
        </div>
    """, unsafe_allow_html=True)

    #uploads the image if there is one 
    if image:
        st.image(image)



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
