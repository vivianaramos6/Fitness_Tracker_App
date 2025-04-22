import streamlit as st
from data_fetcher import (
    get_suggested_goals,
    get_weekly_goals,
    get_completed_goals,
    get_user_achievements,
    get_group_goals,
    check_and_award_goal_achievements,
    mark_goal_as_completed
)

def show_goals_page(user_id):
    st.title("🎯 Your Goals Dashboard")
    st.markdown("Track your progress and stay motivated!")

    if "achievements_checked" not in st.session_state:
        check_and_award_goal_achievements(user_id)
        st.session_state["achievements_checked"] = True

    # 🏆 Achievements (moved up for visibility)
    st.header("🏅 Your Badges & Achievements")
    achievements = get_user_achievements(user_id)

    if not achievements.empty:
        for _, row in achievements.iterrows():
            st.success(f"**{row['Name']}** — {row['Description']} *(Earned: {row['EarnedDate']})*")
    else:
        st.info("You haven’t unlocked any badges yet—complete goals to earn your first one!")


    # 🧠 Suggested Goals
    st.header("🧠 Suggested Goals")

    suggested_goals = get_suggested_goals(user_id)
    if suggested_goals.empty:
        st.info("You're all caught up on suggested goals!")
    else:
        for i, row in suggested_goals.iterrows():
            with st.form(key=f"suggested_goal_{i}", clear_on_submit=True):
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f"**{row['Title']}**")
                with col2:
                    st.markdown(f"🎯 Target: {row['TargetValue']}")
                with col3:
                    submitted = st.form_submit_button("➕ Add")
                    if submitted:
                        from data_fetcher import add_suggested_goal_to_weekly
                        add_suggested_goal_to_weekly(user_id, row["Title"], row["TargetValue"])
                        st.success(f"✅ '{row['Title']}' added to your Weekly Goals!")
                        st.rerun()

    # 👥 Group Goals
    st.header("👥 Group Goals")

    group_goals = get_group_goals(user_id)
    if group_goals.empty:
        st.info("No active group goals.")
    else:
        for i, row in group_goals.iterrows():
            with st.form(key=f"group_goal_{i}", clear_on_submit=True):
                col1, col2, col3 = st.columns([4, 3, 1])
                with col1:
                    st.markdown(f"**{row['GroupName']}**: {row['Description']}")
                with col2:
                    st.markdown(
                        f"Progress: {row['Contribution']}/{row['TargetValue']} | "
                        f"{'✅ Claimed' if row['RewardClaimed'] else '🎯 In Progress'}"
                    )
                with col3:
                    submitted = st.form_submit_button("➕ Add")
                    if submitted:
                        from data_fetcher import add_group_goal_to_weekly
                        add_group_goal_to_weekly(user_id, row["Description"], row["TargetValue"])
                        st.success("✅ Group goal added to your Weekly Goals!")
                        st.rerun()




    # 📅 Weekly Goals
    st.header("📅 Weekly Goals")
    weekly_goals = get_weekly_goals(user_id)

    if weekly_goals.empty:
        st.info("You don’t have any weekly goals set.")
    else:
        for i, row in weekly_goals.iterrows():
            with st.form(key=f"weekly_goal_{i}", clear_on_submit=True):
                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    st.markdown(f"**{row['Title']}**")
                with col2:
                    st.markdown(f"Progress: {row['CurrentValue']} / {row['TargetValue']}")
                with col3:
                    if st.form_submit_button("✅ Mark Completed"):
                        from data_fetcher import mark_goal_as_completed
                        mark_goal_as_completed(user_id, row["Title"])
                        st.success("Goal marked as completed!")
                        st.rerun()


    # Completed Goals
    st.header("✅ Completed Goals")
    st.dataframe(get_completed_goals(user_id), use_container_width=True)



    
if __name__ == "__main__":
    import streamlit as st

    # Fake user ID for testing
    test_user_id = "user1"

    # Display the page as if it's running on its own
    show_goals_page(test_user_id)