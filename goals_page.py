import streamlit as st
from data_fetcher import (
    get_suggested_goals,
    get_weekly_goals,
    get_completed_goals,
    get_user_achievements,
    get_group_goals
)

def show_goals_page(user_id):
    st.title("🎯 Your Goals Dashboard")
    st.markdown("Track your progress and stay motivated!")

    # Suggested Goals
    st.header("🧠 Suggested Goals")
    st.dataframe(get_suggested_goals(user_id), use_container_width=True)

    # Weekly Goals
    st.header("📅 Weekly Goals")
    st.dataframe(get_weekly_goals(user_id), use_container_width=True)

    # Completed Goals
    st.header("✅ Completed Goals")
    st.dataframe(get_completed_goals(user_id), use_container_width=True)

    # Achievements
    st.header("🏆 Achievements")
    st.dataframe(get_user_achievements(user_id), use_container_width=True)

    # Group Goals
    st.header("👥 Group Goals")
    st.dataframe(get_group_goals(user_id), use_container_width=True)


    
if __name__ == "__main__":
    import streamlit as st

    # Fake user ID for testing
    test_user_id = "user1"

    # Display the page as if it's running on its own
    show_goals_page(test_user_id)