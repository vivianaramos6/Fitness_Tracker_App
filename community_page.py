import streamlit as st
from data_fetcher import get_user_profile, get_user_posts
from modules import display_post
from gen_ai_advice import display_genai_advice

def show_community_page(user_id):
    """Displays the community page with friends' posts and GenAI advice"""
    
    # Page header
    st.title("Community Feed")
    st.markdown("---")
    
    # Get user profile and friends list
    user_profile = get_user_profile(user_id)
    
    if not user_profile:
        st.error("User profile not found")
        return
    
    # Section 1: GenAI Advice
    st.header("✨ Your Daily Motivation")
    display_genai_advice(
        "2025-03-09 10:00",
        "Set a small goal, like 5 minutes of movement. Once you start, you'll likely keep going! 'Discipline is choosing between what you want now and what you want most.'",
        "assets/images/motivation.jpeg"
    )
    st.markdown("---")
    #/home/aceni31/A3_team_repo1/.vscode/vivianaramos6techx25-b75c1c04b0e4.json
    
    # Section 2: Friends' Posts
    st.header("👥 Friends' Activity")
    
    # Get posts from all friends
    all_friends_posts = []
    for friend_id in user_profile['friends']:
        friend_posts = get_user_posts(friend_id)
        all_friends_posts.extend(friend_posts)
    
    # Sort all posts by timestamp (newest first)
    all_friends_posts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Display first 10 posts
    if not all_friends_posts:
        st.info("No posts from friends yet. Be the first to post!")
    else:
        for post in all_friends_posts[:10]:
            display_post(
                username=post['username'],
                user_image=post['user_image'],
                timestamp=post['timestamp'],
                content=post['content'],
                post_image=post['image']
            )
    
    # Refresh button
    if st.button("🔄 Refresh Feed"):
        st.rerun()

# Example usage (for testing)
if __name__ == "__main__":
    show_community_page("user1")  # Replace with actual user ID when integrating