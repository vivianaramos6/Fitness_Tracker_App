import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

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
            with advice_container: 
                display_genai_advice(
                    "2025-03-09 10:00",
                    "Set a small goal, like 5 minutes of movement. Once you start, you'll likely keep going! 'Discipline is choosing between what you want now and what you want most.'",
                    "assets/images/motivation.jpeg"
                )
            