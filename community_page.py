import streamlit as st
from data_fetcher import get_user_profile, get_user_posts, get_genai_advice
from modules import display_post, display_genai_advice

def show_community_page(user_id):
    """Displays the community page with friends' posts and GenAI advice"""
    
    try:
        # Page header
        st.title("Community Feed")
        st.markdown("---")
        
        # Section 1: GenAI Advice
        st.header("✨ Your Daily Motivation")
        advice = get_genai_advice(user_id)
        display_genai_advice(
            advice['timestamp'],
            advice['content'],
            advice['image_url']
        )
        st.markdown("---")
        
        # Section 2: Friends' Posts
        st.header("👥 Friends' Activity")
        
        # Get user profile and friends list
        user_profile = get_user_profile(user_id)
        if not user_profile:
            st.error("User profile not found")
            return
            
        all_friends_posts = []
        for friend_id in user_profile.get('friends', []):
            try:
                friend_posts = get_user_posts(friend_id)
                if friend_posts:
                    all_friends_posts.extend(friend_posts)
            except Exception as e:
                st.warning(f"Couldn't load posts for friend {friend_id}")
                continue
        
        # Sort and display posts
        if all_friends_posts:
            # Sort by timestamp (newest first)
            all_friends_posts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            for post in all_friends_posts[:10]:
                display_post(
                    username=post.get('username', 'Unknown'),
                    user_image=post.get('user_image', 'https://via.placeholder.com/50'),
                    timestamp=post.get('timestamp', ''),
                    content=post.get('content', ''),
                    post_image=post.get('image')
                )
        else:
            st.info("No posts from friends yet. Be the first to post!")
        
        # Refresh button
        if st.button("🔄 Refresh Feed", key="refresh_feed"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading community page: {str(e)}")
