import streamlit as st
from google.cloud import bigquery
import pandas as pd
from datetime import datetime, time as dtime, timezone, timedelta
import uuid
import calendar

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aceni31/A3_team_repo1/.vscode/vivianaramos6techx25-b75c1c04b0e4.json"

# Free stock image URLs for different categories
GROUP_IMAGES = {
    "Cycling": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=300",
    "Running": "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=300",
    "Yoga": "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=300",
    "Weightlifting": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300",
    "Default": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=300"
}

def get_group_image(category):
    """Returns appropriate free-to-use image based on group category"""
    return GROUP_IMAGES.get(category, GROUP_IMAGES["Default"])

def get_member_count(client, group_id):
    """Helper function to get member count for a group"""
    query = f"""
        SELECT COUNT(*) as member_count
        FROM `vivianaramos6techx25.ISE.GroupMemberships`
        WHERE GroupId = '{group_id}'
    """
    result = client.query(query).to_dataframe()
    return result.iloc[0]['member_count']

def get_client():
    PROJECT_ID = "vivianaramos6techx25"
    DATASET_ID = "ISE"
    client = bigquery.Client(project=PROJECT_ID)
    return bigquery.Client(project=PROJECT_ID)

def get_user_name(user_id):
    try:
        query = f"""
            SELECT Name
            FROM `{PROJECT_ID}.{DATASET_ID}.Users`
            WHERE LOWER(UserId) = LOWER(@user_id)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
        client = get_client()
        results = client.query(query, job_config=job_config).result()
        row = next(iter(results), None)
        return row.Name if row else "Unknown User"
    except Exception as e:
        st.error(f"Error retrieving user name: {e}")
        return "Unknown User"

def get_group_users(user_id):
    try:
        query = f"""
            SELECT DISTINCT U.UserId, U.Name
            FROM `{PROJECT_ID}.{DATASET_ID}.Users` U
            JOIN `{PROJECT_ID}.{DATASET_ID}.GroupMemberships` GM 
            ON U.UserId = GM.UserId
            WHERE GM.GroupId IN (
                SELECT GroupId
                FROM `{PROJECT_ID}.{DATASET_ID}.GroupMemberships`
                WHERE LOWER(UserId) = LOWER(@user_id)
            )
            AND LOWER(U.UserId) != LOWER(@user_id)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
        client = get_client()
        results = client.query(query, job_config=job_config).result()
        return [(row.UserId, row.Name) for row in results]
    except Exception as e:
        st.error(f"Error retrieving group members: {e}")
        return []

def get_group_events():
    try:
        query = f"""
            SELECT EventId, Title, EventDate
            FROM `{PROJECT_ID}.{DATASET_ID}.GroupEvents`
            ORDER BY EventDate
        """
        client = get_client()
        results = client.query(query).result()
        return pd.DataFrame([(row.EventId, row.Title, row.EventDate) 
                            for row in results], 
                            columns=['EventId', 'Title', 'EventDate'])
    except Exception as e:
        st.error(f"Error retrieving events: {e}")
        return pd.DataFrame([], columns=['EventId', 'Title', 'EventDate'])

def create_event(title, event_datetime, duration, user_id, invitees):
    try:
        event_id = str(uuid.uuid4())

        query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.GroupEvents` 
            (EventId, Title, EventDate) 
            VALUES (@event_id, @title, @event_date)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("event_id", "STRING", event_id),
                bigquery.ScalarQueryParameter("title", "STRING", title),
                bigquery.ScalarQueryParameter("event_date", "DATETIME", event_datetime),
            ]
        )
        client = get_client()
        client.query(query, job_config=job_config).result()

        try:
            for invitee_id in invitees:
                join_query = f"""
                    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.GroupEventInvitees` 
                    (EventId, UserId) 
                    VALUES (@event_id, @invitee_id)
                """
                join_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("event_id", "STRING", event_id),
                        bigquery.ScalarQueryParameter("invitee_id", "STRING", invitee_id),
                    ]
                )       
                client.query(join_query, join_config).result()
        except Exception:
            pass

        return event_id
    except Exception as e:
        st.error(f"Error creating event: {e}")
        return None

def is_user_group_admin(user_id, group_id):
    try:
        query = f"""
            SELECT IsAdmin
            FROM `{PROJECT_ID}.{DATASET_ID}.GroupMemberships`
            WHERE UserId = @user_id AND GroupId = @group_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
            ]
        )
        client = get_client()
        result = client.query(query, job_config=job_config).to_dataframe()
        return not result.empty and result.iloc[0]['IsAdmin']
    except Exception as e:
        st.error(f"Error checking admin status: {e}")
        return False

def display_fitness_groups(user_id):
    """Display a centralized group management hub with clear visual differentiation"""
    client = get_client()
    # Initialize BigQuery client
    
    # --- DATABASE QUERIES ---
    # Get all available groups
    all_groups_query = f"""
        SELECT GroupId, Name, Description, Category
        FROM `vivianaramos6techx25.ISE.FitnessGroups`
    """
    
    # Get user's joined groups
    joined_groups_query = f"""
        SELECT g.GroupId, g.Name, g.Description, g.Category, 
               gm.JoinedDate, gm.IsAdmin
        FROM `vivianaramos6techx25.ISE.FitnessGroups` g
        JOIN `vivianaramos6techx25.ISE.GroupMemberships` gm
        ON g.GroupId = gm.GroupId
        WHERE gm.UserId = '{user_id}'
        ORDER BY gm.JoinedDate DESC
    """

    try:
        all_groups = client.query(all_groups_query).to_dataframe()
        joined_groups = client.query(joined_groups_query).to_dataframe()
        
        # Add member_count to all_groups
        all_groups['member_count'] = all_groups['GroupId'].apply(lambda x: get_member_count(client, x))
        
        # Add member_count to joined_groups
        joined_groups['member_count'] = joined_groups['GroupId'].apply(lambda x: get_member_count(client, x))
        
    except Exception as e:
        st.error(f"Error loading groups: {str(e)}")
        return
    
    # --- UI IMPLEMENTATION ---
    st.title("🏋️ Fitness Groups Hub")
    
    # Tab system for better navigation
    tab1, tab2, tab3 = st.tabs(["My Groups", "Discover Groups", "Group Calendar"])
    
    with tab1:
        # MY GROUPS SECTION (joined groups)
        if not joined_groups.empty:
            st.header("Your Fitness Communities")
            st.caption("Groups you've joined - click to manage")
            
            # Display joined groups with images
            for _, group in joined_groups.iterrows():
                with st.container(border=True):
                    cols = st.columns([1, 4, 1])
                    with cols[0]:
                        st.image(
                            get_group_image(group['Category']),
                            width=120,
                            caption=group['Category']
                        )
                    with cols[1]:
                        # Make the group name clickable
                        if st.button(
                            group['Name'],
                            key=f"group_{group['GroupId']}",
                            help="Click to view group details"
                        ):
                            st.session_state.current_group = group['GroupId']
                            st.rerun()
                            
                        st.caption(f"👥 {group['member_count']} members • Joined on {group['JoinedDate'].strftime('%b %d, %Y')}")
                        st.write(group['Description'])
                    with cols[2]:
                        if group['IsAdmin']:
                            st.markdown("👑 **Admin**")
                        if st.button("🚪 Leave Group", 
                                   key=f"leave_{group['GroupId']}",
                                   use_container_width=True):
                            leave_group(user_id, group['GroupId'])
                            st.rerun()
        else:
            st.info("You haven't joined any groups yet. Explore groups below!")
            st.image(
                "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500",
                width=400
            )
    
    with tab2:
        # DISCOVER GROUPS SECTION (all available groups)
        st.header("Discover Fitness Communities")
        st.caption("Find groups that match your interests")
        
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(
                "Filter by category",
                ["All"] + list(all_groups['Category'].unique()))
        with col2:
            search_term = st.text_input("Search groups")
        
        filtered_groups = all_groups.copy()
        if category_filter != "All":
            filtered_groups = filtered_groups[filtered_groups['Category'] == category_filter]
        if search_term:
            filtered_groups = filtered_groups[
                filtered_groups['Name'].str.contains(search_term, case=False) |
                filtered_groups['Description'].str.contains(search_term, case=False)
            ]
        
        if not filtered_groups.empty:
            # Group by category for better organization
            for category, group in filtered_groups.groupby('Category'):
                st.subheader(f"{category} Groups")
                group_chunks = [group[i:i+3] for i in range(0, len(group), 3)]
                
                for chunk in group_chunks:
                    cols = st.columns(3)
                    for idx, (_, group) in enumerate(chunk.iterrows()):
                        with cols[idx]:
                            with st.container(border=True):
                                st.image(
                                    get_group_image(group['Category']),
                                    use_container_width=True
                                )
                                st.subheader(group['Name'])
                                st.caption(f"👥 {group['member_count']} members")
                                st.write(group['Description'][:100] + "...")
                                
                                if group['GroupId'] not in joined_groups['GroupId'].values:
                                    if st.button(
                                        "➕ Join Group",
                                        key=f"join_{group['GroupId']}",
                                        use_container_width=True
                                    ):
                                        join_group(user_id, group['GroupId'])
                                        st.rerun()
                                else:
                                    st.success("✓ Joined", icon="✅")
        else:
            st.warning("No groups match your filters")
            
    with tab3:
        # CALENDAR SECTION
        st.header("📅 Group Workouts Calendar")
        
        if not joined_groups.empty:
            try:
                # Display calendar date picker first
                selected_date = st.date_input(
                    "Select a date to view events",
                    datetime.today(),
                    key="calendar_date"
                )
                
                # Get events for the selected date only (more efficient query)
                events_query = f"""
                    SELECT 
                        e.EventId, 
                        e.Title, 
                        e.EventDate, 
                        e.Location, 
                        e.Description, 
                        g.Name as GroupName, 
                        g.GroupId,
                        g.Category,
                        COUNT(gm.UserId) as MemberCount
                    FROM `vivianaramos6techx25.ISE.GroupEvents` e
                    JOIN `vivianaramos6techx25.ISE.FitnessGroups` g
                        ON e.GroupId = g.GroupId
                    JOIN `vivianaramos6techx25.ISE.GroupMemberships` gm
                        ON g.GroupId = gm.GroupId
                    WHERE g.GroupId IN (
                        SELECT GroupId 
                        FROM `vivianaramos6techx25.ISE.GroupMemberships` 
                        WHERE UserId = '{user_id}'
                    )
                    AND DATE(e.EventDate) = DATE('{selected_date}')
                    GROUP BY e.EventId, e.Title, e.EventDate, e.Location, e.Description, g.Name, g.GroupId, g.Category
                    ORDER BY e.EventDate
                """
                
                events_df = client.query(events_query).to_dataframe()
                
                if not events_df.empty:
                    st.subheader(f"Events on {selected_date.strftime('%A, %B %d, %Y')}")
                    
                    for _, event in events_df.iterrows():
                        # Convert to datetime if not already
                        event_date = pd.to_datetime(event['EventDate'])
                        
                        with st.container(border=True):
                            cols = st.columns([1, 3])
                            with cols[0]:
                                st.image(
                                    get_group_image(event['Category']),
                                    width=120
                                )
                            with cols[1]:
                                st.markdown(f"#### {event['Title']}")
                                st.caption(f"⏰ {event_date.strftime('%I:%M %p')} | 📍 {event['Location']}")
                                st.caption(f"👥 {event['MemberCount']} group members | 🏷️ {event['GroupName']}")
                                st.write(event['Description'])
                                
                                if st.button(
                                    "View Group",
                                    key=f"view_{event['GroupId']}_{event['EventId']}",
                                    help=f"Go to {event['GroupName']} group page"
                                ):
                                    st.session_state.current_group = event['GroupId']
                                    st.rerun()
                else:
                    st.info(f"No events scheduled for {selected_date.strftime('%A, %B %d, %Y')}")
                # else:
                #     st.info("No upcoming events found in your groups")
                    
                # Schedule new event section
                st.divider()
                with st.expander("➕ Schedule New Group Workout", expanded=False):
                    with st.form("new_workout_form"):
                        group_id = st.selectbox(
                            "Select Group",
                            options=joined_groups['GroupId'],
                            format_func=lambda x: joined_groups[joined_groups['GroupId'] == x]['Name'].values[0]
                        )
                        title = st.text_input("Workout Title*", placeholder="Morning Run, Yoga Session, etc.")
                        workout_date = st.date_input("Date*", min_value=datetime.today())
                        workout_time = st.time_input("Time*")
                        location = st.text_input("Location", placeholder="Central Park, Beachfront, etc.")
                        description = st.text_area("Description", placeholder="Describe the workout session...")
                        
                        if st.form_submit_button("Schedule Workout"):
                            if not title:
                                st.error("Title is required")
                            else:
                                workout_datetime = datetime.combine(workout_date, workout_time)
                                if schedule_group_workout(
                                    group_id,
                                    user_id,
                                    workout_datetime,
                                    location,
                                    title,
                                    description
                                ):
                                    st.success("Workout scheduled successfully!")
                                    st.rerun()
            

            except Exception as e:
                st.error(f"Error loading events: {str(e)}")
                st.error("Please check if the GroupEvents table exists and contains data")
        else:
            st.info("You haven't joined any groups yet. Join groups to see and schedule workouts.")
            st.image(
                "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=500",
                width=400
            )

        
def handle_group_membership(user_id, group_id, action):
    """
    Unified function to handle group joining/leaving with improved user feedback
    based on usability test findings.
    
    Args:
        user_id: Current user's ID
        group_id: Target group ID
        action: 'join' or 'leave'
    """
    client = get_client()
    
    try:
        if action == 'join':
            # Check if already a member first
            check_query = f"""
                SELECT COUNT(*) as is_member
                FROM `vivianaramos6techx25.ISE.GroupMemberships`
                WHERE UserId = '{user_id}' AND GroupId = '{group_id}'
            """
            result = client.query(check_query).to_dataframe()
            
            if not result.empty and result.iloc[0]['is_member'] > 0:
                st.warning("You're already a member of this group!")
                return False
            
            group_query = f"""
                SELECT Name FROM `vivianaramos6techx25.ISE.FitnessGroups`
                WHERE GroupId = '{group_id}'
            """
            group_name = client.query(group_query).to_dataframe().iloc[0]['Name']
            
            join_query = f"""
                INSERT INTO `vivianaramos6techx25.ISE.GroupMemberships`
                (GroupId, UserId, JoinedDate, IsAdmin)
                VALUES ('{group_id}', '{user_id}', CURRENT_DATE(), FALSE)
            """
            client.query(join_query)
            
            st.success(f"🎉 Welcome to {group_name}! You've joined successfully.")
            return True
            
        elif action == 'leave':
            # Get group name for feedback
            group_query = f"""
                SELECT g.Name, gm.IsAdmin
                FROM `vivianaramos6techx25.ISE.FitnessGroups` g
                JOIN `vivianaramos6techx25.ISE.GroupMemberships` gm
                ON g.GroupId = gm.GroupId
                WHERE gm.UserId = '{user_id}' AND gm.GroupId = '{group_id}'
            """
            result = client.query(group_query).to_dataframe()
            
            if result.empty:
                st.error("You're not a member of this group")
                return False
                
            group_name = result.iloc[0]['Name']
            is_admin = result.iloc[0]['IsAdmin']
            
            if is_admin:
                st.warning("⚠️ You're an admin of this group. Please assign a new admin before leaving.")
                return False
                
            leave_query = f"""
                DELETE FROM `vivianaramos6techx25.ISE.GroupMemberships`
                WHERE UserId = '{user_id}' AND GroupId = '{group_id}'
            """
            client.query(leave_query)
            
            st.success(f"👋 You've left {group_name}. Hope to see you again soon!")
            return True
            
        else:
            st.error("Invalid action specified")
            return False
            
    except Exception as e:
        st.error(f"Error handling group membership: {str(e)}")
        return False

def leave_group(user_id, group_id):
    """Handle leaving a group"""
    return handle_group_membership(user_id, group_id, 'leave')

def join_group(user_id, group_id):
    """Handle joining a group"""
    return handle_group_membership(user_id, group_id, 'join')

def schedule_group_workout(group_id, user_id, workout_datetime, location=None, title="Group Workout", description=""):
    """Handle scheduling of joint workouts for fitness groups"""
    
    client = get_client()
    
    try:
        event_id = f"event_{group_id}_{workout_datetime.strftime('%Y%m%d%H%M')}"
        
        if not location:
            location_value = 'NULL'
        else:
            escaped_location = location.replace("'", "''")
            location_value = f"'{escaped_location}'"
        
        insert_query = f"""
            INSERT INTO `vivianaramos6techx25.ISE.GroupEvents`
            (EventId, GroupId, Title, Description, EventDate, Location, MaxParticipants, CreatorId)
            VALUES (
                '{event_id}',
                '{group_id}',
                '{title.replace("'", "''")}',
                '{description.replace("'", "''")}',
                '{workout_datetime.strftime('%Y-%m-%d %H:%M:%S')}',
                {location_value},
                20,
                '{user_id}'
            )
        """
        
        job = client.query(insert_query)
        job.result()
        st.success("✅ Workout scheduled successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to schedule workout: {str(e)}")
        return False


def rsvp_to_workout(user_id, event_id):
    """Handle RSVP to a workout event"""
    client = get_client()
    
    try:
        # Check if already RSVP'd
        check_query = f"""
            SELECT COUNT(*) as count
            FROM `vivianaramos6techx25.ISE.EventAttendees`
            WHERE UserId = '{user_id}' AND EventId = '{event_id}'
        """
        result = client.query(check_query).to_dataframe()
        
        if result.iloc[0]['count'] > 0:
            st.warning("You're already signed up for this workout")
            return False
            
        # Add RSVP
        insert_query = f"""
            INSERT INTO `vivianaramos6techx25.ISE.EventAttendees`
            (EventId, UserId, RSVPDate)
            VALUES ('{event_id}', '{user_id}', CURRENT_TIMESTAMP())
        """
        client.query(insert_query)
        return True
        
    except Exception as e:
        st.error(f"Failed to RSVP: {str(e)}")
        return False

def is_event_creator(client, user_id, event_id):
    """Check if user created this event"""
    query = f"""
        SELECT COUNT(*) as is_creator
        FROM `vivianaramos6techx25.ISE.GroupEvents`
        WHERE EventId = '{event_id}'
        AND CreatorId = '{user_id}'
    """
    result = client.query(query).to_dataframe()
    return result.iloc[0]['is_creator'] > 0

def has_rsvped(client, user_id, event_id):
    """Check if user already RSVP'd"""
    query = f"""
        SELECT COUNT(*) as has_rsvp
        FROM `vivianaramos6techx25.ISE.EventAttendees`
        WHERE UserId = '{user_id}' AND EventId = '{event_id}'
    """
    result = client.query(query).to_dataframe()
    return result.iloc[0]['has_rsvp'] > 0

def display_group_page(group_id, user_id):
    """Display an individual group page with members, workout scheduling, and management"""
    
    client = get_client()
    
    # --- DATABASE QUERIES ---
    group_query = f"""
        SELECT g.GroupId, g.Name, g.Description, g.Category,
               gm.JoinedDate, gm.IsAdmin
        FROM `vivianaramos6techx25.ISE.FitnessGroups` g
        LEFT JOIN `vivianaramos6techx25.ISE.GroupMemberships` gm
        ON g.GroupId = gm.GroupId AND gm.UserId = '{user_id}'
        WHERE g.GroupId = '{group_id}'
    """
    
    # Get group members with count
    members_query = f"""
        WITH member_count AS (
            SELECT COUNT(*) as count 
            FROM `vivianaramos6techx25.ISE.GroupMemberships`
            WHERE GroupId = '{group_id}'
        )
        SELECT u.UserId, u.Name, u.ImageUrl, gm.JoinedDate, gm.IsAdmin,
               (SELECT count FROM member_count) as member_count
        FROM `vivianaramos6techx25.ISE.Users` u
        JOIN `vivianaramos6techx25.ISE.GroupMemberships` gm
        ON u.UserId = gm.UserId
        WHERE gm.GroupId = '{group_id}'
        ORDER BY gm.JoinedDate
    """
    
    workouts_query = f"""
        SELECT EventId, Title, Description, EventDate, Location, MaxParticipants
        FROM `vivianaramos6techx25.ISE.GroupEvents`
        WHERE EventDate >= CURRENT_DATETIME()
        ORDER BY EventDate
        LIMIT 3
    """
    
    try:
        group_df = client.query(group_query).to_dataframe()
        members_df = client.query(members_query).to_dataframe()
        workouts_df = client.query(workouts_query).to_dataframe()
        
        if group_df.empty:
            st.error("Group not found")
            return
            
        group = group_df.iloc[0]
        is_member = not pd.isna(group['JoinedDate'])
        is_admin = group.get('IsAdmin', False)

        member_count = members_df.iloc[0]['member_count'] if not members_df.empty else 0
        
    except Exception as e:
        st.error(f"Error loading group data: {str(e)}")
        return
    
    # --- UI IMPLEMENTATION ---
    st.title(f"🏋️ {group['Name']}")
    st.caption(f"{group['Category']} Group • 👥 {member_count} members")
    
    # Group header with image and description
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            get_group_image(group['Category']),
            width=200
        )
    with col2:
        st.write(group['Description'])
        
        # Membership status and actions
        if is_member:
            st.success("✓ You are a member of this group")
            if st.button("🚪 Leave Group", key="leave_group"):
                if leave_group(user_id, group_id):
                    st.rerun()
        else:
            st.warning("You're not a member of this group")
            if st.button("➕ Join Group", key="join_group"):
                if join_group(user_id, group_id):
                    st.rerun()
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Members", "Upcoming Workouts", "Group Info"])
    
    with tab1:
        # MEMBERS SECTION
        st.subheader(f"👥 Group Members ({member_count})")
        
        if not members_df.empty:
            # Display 3 members per row
            member_chunks = [members_df[i:i+3] for i in range(0, len(members_df), 3)]
            
            for chunk in member_chunks:
                cols = st.columns(3)
                for idx, (_, member) in enumerate(chunk.iterrows()):
                    with cols[idx]:
                        with st.container(border=True):
                            st.image(
                                member['ImageUrl'] or "https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=150",
                                width=100
                            )
                            st.write(f"**{member['Name']}**")
                            st.caption(f"Joined: {member['JoinedDate'].strftime('%b %Y')}")
                            if member['IsAdmin']:
                                st.markdown("👑 **Admin**")
        # use_column_width
        else:
            st.info("No members found in this group")
    
    with tab2:
        # WORKOUTS SECTION
        st.subheader("🏃 Upcoming Workouts")
        
        if not workouts_df.empty:
            client = bigquery.Client(project="vivianaramos6techx25")
            for _, workout in workouts_df.iterrows():
                with st.container(border=True):
                    st.write(f"**{workout['Title']}**")
                    st.caption(f"📅 {workout['EventDate'].strftime('%A, %b %d %Y at %I:%M %p')}")
                    st.caption(f"📍 {workout['Location']}")
                    st.write(workout['Description'])
                    
                    if is_member:
                        creator_status = is_event_creator(client, user_id, workout['EventId'])
                        rsvp_status = has_rsvped(client, user_id, workout['EventId'])
                        
                        if creator_status:
                            st.info("👑 You created this event")
                        elif rsvp_status:
                            st.success("✅ You're attending this event")
                        else:
                            if st.button("✋ I'll Attend", key=f"rsvp_{workout['EventId']}"):
                                if rsvp_to_workout(user_id, workout['EventId']):
                                    st.rerun()
        
        # Schedule new workout form
        if is_member:
            st.divider()
            with st.expander("📅 Schedule New Workout"):
                with st.form("schedule_workout"):
                    title = st.text_input("Workout Title*", value="Group Workout")
                    date = st.date_input("Date*", min_value=datetime.now().date())
                    time = st.time_input("Time*")
                    location = st.text_input("Location")
                    description = st.text_area("Description", 
                                             value="Join your fellow group members for a workout session!")
                    
                    if st.form_submit_button("Schedule Workout"):
                        if not title:
                            st.error("Title is required")
                        else:
                            workout_datetime = datetime.combine(date, time)
                            if schedule_group_workout(
                                group_id,
                                user_id,
                                workout_datetime,
                                location,
                                title,
                                description
                            ):
                                st.rerun()
        else:
            st.info("Join the group to see and schedule workouts")
    
    with tab3:
        # GROUP INFO SECTION
        st.subheader("ℹ️ Group Information")
        
        st.write(f"**Category:** {group['Category']}")
        st.write(f"**Members:** {member_count}")  # Changed from group['member_count'] to member_count
        st.write(f"**Created:** {group['JoinedDate'].strftime('%B %Y') if not pd.isna(group['JoinedDate']) else 'Unknown'}")
        
        # Admin controls
        if is_admin:
            st.divider()
            st.subheader("Admin Tools")
            
            with st.expander("⚙️ Group Settings"):
                new_name = st.text_input("Group Name", value=group['Name'])
                new_desc = st.text_area("Description", value=group['Description'])
                
                if st.button("Update Group"):
                    # Implement update logic
                    st.success("Group updated successfully!")
            
            with st.expander("⚠️ Danger Zone"):
                if st.button("🚨 Delete Group", type="secondary"):
                    st.error("Are you sure you want to delete this group?")
                    if st.button("✅ Confirm Delete"):
                        # Implement delete logic
                        st.success("Group deleted successfully")
                        st.rerun()

