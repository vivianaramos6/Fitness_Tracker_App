#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel, GenerationConfig
# from vertexai.language_models import ChatModel
from google.cloud import aiplatform
from datetime import date, timedelta
import vertexai
import uuid
import os
import random
import datetime

# users = {
#     'user1': {
#         'full_name': 'Remi',
#         'username': 'remi_the_rems',
#         'date_of_birth': '1990-01-01',
#         'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
#         'friends': ['user2', 'user3', 'user4'],
#     },
#     'user2': {
#         'full_name': 'Blake',
#         'username': 'blake',
#         'date_of_birth': '1990-01-01',
#         'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
#         'friends': ['user1'],
#     },
#     'user3': {
#         'full_name': 'Jordan',
#         'username': 'jordanjordanjordan',
#         'date_of_birth': '1990-01-01',
#         'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
#         'friends': ['user1', 'user4'],
#     },
#     'user4': {
#         'full_name': 'Gemmy',
#         'username': 'gems',
#         'date_of_birth': '1990-01-01',
#         'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
#         'friends': ['user1', 'user3'],
#     },
# }


def get_user_sensor_data(user_id, workout_id):
    """
    Returns a list of sensor data from the workout.
    
    Each item in the list is a dictionary with:
    - sensor_type: Name of the sensor (e.g., Heart Rate)
    - timestamp: When the sensor recorded the value
    - data: The value recorded
    - units: The unit of measurement (e.g., bpm)
    """
    PROJECT_ID = "vivianaramos6techx25"
    DATASET_ID = "ISE"
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT 
            st.Name AS sensor_type,
            sd.Timestamp AS timestamp,
            sd.SensorValue AS data,
            st.Units AS units
        FROM `{PROJECT_ID}.{DATASET_ID}.SensorData` sd
        JOIN `{PROJECT_ID}.{DATASET_ID}.SensorTypes` st
          ON sd.SensorId = st.SensorId
        JOIN `{PROJECT_ID}.{DATASET_ID}.Workouts` w
          ON sd.WorkoutID = w.WorkoutId
        WHERE w.UserId = @user_id AND sd.WorkoutID = @workout_id
        ORDER BY timestamp
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    sensor_data_list = []
    for row in results:
        sensor_data_list.append({
            "sensor_type": row.sensor_type,
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "data": row.data,
            "units": row.units
        })

    return sensor_data_list

def get_user_workouts(user_id):
    """
    Fetches a list of workouts for a given user from the BigQuery database.
    
    Args:
        user_id (str): The ID of the user.
    
    Returns:
        List[dict]: A list of dictionaries representing workouts with keys:
            workout_id, start_timestamp, end_timestamp, start_lat_lng, 
            end_lat_lng, distance, steps, and calories_burned.
    """
    # Set your project and dataset
    project_id = "vivianaramos6techx25"       # Replace with your actual project ID
    dataset_id = "ISE"      # Replace with your actual dataset name

    client = bigquery.Client(project=project_id)

    query = f"""
        SELECT 
            WorkoutId AS workout_id,
            FORMAT_DATETIME('%Y-%m-%d %H:%M:%S', StartTimestamp) AS start_timestamp,
            FORMAT_DATETIME('%Y-%m-%d %H:%M:%S', EndTimestamp) AS end_timestamp,
            [StartLocationLat, StartLocationLong] AS start_lat_lng,
            [EndLocationLat, EndLocationLong] AS end_lat_lng,
            TotalDistance AS distance,
            TotalSteps AS steps,
            CaloriesBurned AS calories_burned
        FROM `{project_id}.{dataset_id}.Workouts`
        WHERE UserId = @user_id
        ORDER BY StartTimestamp DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    workouts = []
    for row in results:
        workouts.append({
            "workout_id": row.workout_id,
            "start_timestamp": row.start_timestamp,
            "end_timestamp": row.end_timestamp,
            "start_lat_lng": row.start_lat_lng,
            "end_lat_lng": row.end_lat_lng,
            "distance": row.distance,
            "steps": row.steps,
            "calories_burned": row.calories_burned
        })

    return workouts


def get_user_profile(user_id):
    """Returns profile information for a given user including their friends list.
    
    Args:
        user_id (str): The ID of the user whose profile we want to retrieve
        
    Returns:
        dict: A dictionary with keys:
              - full_name
              - username
              - date_of_birth (as string)
              - profile_image
              - friends (list of friend user_ids)
    """

    from google.cloud import bigquery

    # Initialize BigQuery client with explicit project ID
    client = bigquery.Client(project="vivianaramos6techx25")  

    profile_query = f"""
        SELECT 
            Name as full_name,
            Username as username,
            CAST(DateOfBirth AS STRING) as date_of_birth,
            ImageUrl as profile_image
        FROM 
            `{client.project}.ISE.Users`
        WHERE 
            UserId = '{user_id}'
    """

    # Query to get friends list
    friends_query = f"""
        SELECT 
            CASE
                WHEN UserId1 = '{user_id}' THEN UserId2
                ELSE UserId1
            END as friend_id
        FROM 
            `{client.project}.ISE.Friends`
        WHERE 
            UserId1 = '{user_id}' OR UserId2 = '{user_id}'
    """
    
    # Execute queries...
    profile_job = client.query(profile_query)
    profile_result = list(profile_job.result())
    
    if not profile_result:
        return None  # User not found
    
    # Execute friends query
    friends_job = client.query(friends_query)
    friends_result = list(friends_job.result())
    
    # Prepare the result dictionary
    user_profile = {
        'full_name': profile_result[0].full_name,
        'username': profile_result[0].username,
        'date_of_birth': profile_result[0].date_of_birth,
        'profile_image': profile_result[0].profile_image,
        'friends': [row.friend_id for row in friends_result]
    }
    
    return user_profile



def get_user_posts(user_id):
    """Returns a list of a user's posts from the database.
    
    Args:
        user_id (str): The ID of the user whose posts we want to retrieve
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a post with keys:
              user_id, post_id, timestamp, content, and image
    """
    from google.cloud import bigquery


    # Initialize BigQuery client with explicit project
    client = bigquery.Client(project="vivianaramos6techx25")
    
    # Query to get posts for the specified user
    query = f"""
        SELECT 
            p.PostId as post_id,
            p.AuthorId as user_id,
            p.Timestamp as timestamp,
            p.Content as content,
            p.ImageUrl as image,
            u.ImageUrl as user_image,
            u.Username as username
        FROM 
            `vivianaramos6techx25.ISE.Posts` p  
        JOIN
            `vivianaramos6techx25.ISE.Users` u  
        ON
            p.AuthorId = u.UserId
        WHERE 
            p.AuthorId = '{user_id}'
        ORDER BY
            p.Timestamp DESC
    """
    
    # Execute the query with timeout
    query_job = client.query(query)
    results = query_job.result() 
    
    # Convert results to list of dictionaries
    posts = []
    for row in results:
        post = {
            'user_id': row.user_id,
            'post_id': row.post_id,
            'timestamp': str(row.timestamp),
            'content': row.content if row.content else "",
            'image': row.image if row.image else None,
            'username': row.username,
            'user_image': row.user_image
        }
        posts.append(post)
    
    return posts


def get_genai_advice(user_id, user_input="Give me fitness advice"):
    """Get personalized fitness advice from Vertex AI Gemini."""
    try:
        #Used AI to help debug to get the users info from the query as well as help generate query code
        project_id = "vivianaramos6techx25"
        dataset_id = "ISE"
        client = bigquery.Client(project=project_id)
                
        query = """
            SELECT Name AS name
            FROM `vivianaramos6techx25.ISE.Users`
            WHERE LOWER(UserId) = LOWER(@user_id)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
        query_job = client.query(query, job_config=job_config)
        result = list(query_job.result())
        #print(f"Running query: {query}")
        #print(f"BigQuery result: {result}")
        #Needs to access like 2 d array to get the users information from the query table!!
        user_name = result[0][0] if result else "User"

        workouts = get_user_workouts(user_id)
        include_image = len(workouts) < 2
        
        vertexai.init(project=project_id, location="us-central1")
        model = GenerativeModel("gemini-2.0-flash")
        
        #response and instructions for the fitness bot. prompt is extensive because without a detailed prompt
        #the bot would give the same fitness advice each time its asked
        prompt = f"""You're a fitness coach. {user_name} asks: "{user_input}"
        Respond with fitness advice based off what the user is asking you.
        For example, if the user asks for a fitness quote to keep them motivated provide them a fitness quote.
        Also make the advice or quote short, 1-2 sentences.
        If the user does not specify exactly what they want give generic fitness advice."""
        
        response = model.generate_content(prompt)
        content = response.text if hasattr(response, 'text') else "Stay active!"

        timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M')
        simple_advice_id = f"adv_{user_id}_{timestamp_str}"
        image_url = 'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'         
        return {
            'advice_id': simple_advice_id,    
            'content': f"{user_name}, {content}",
            'image_url': image_url if include_image else None, 
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
    except Exception as e:
        return {
            'advice_id': f"adv_{user_id}_error",  # Include user ID even in error case
            'content': "Sorry, I couldn't generate advice right now.",
            'image_url': None,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }



def get_suggested_goals(user_id): 
    
    vertexai.init(project="vivianaramos6techx25", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")
    import pandas as pd
    import streamlit as st

    client = bigquery.Client(project="vivianaramos6techx25")

    # Prompt Gemini to generate 10 generic weekly fitness goals
    prompt = (
        "Generate 10 weekly fitness goals that are simple and measurable. "
        "Format each as: Goal Title - Target Value.\n\n"
        "Example:\n"
        "Run 10 miles - 10\n"
        "Drink 8 cups of water - 8\n"
        "Now generate the full list:"
    )

    response = model.generate_content(prompt)
    goals_text = response.text.strip()

    # Parse into a dataframe format
    generic_goals = []
    for line in goals_text.splitlines():
        if "-" in line:
            parts = line.split("-", 1)
            title = parts[0].strip("•*1234567890. ").strip()
            value = parts[1].strip()
            try:
                numeric_value = float(''.join([c for c in value if c.isdigit() or c == '.']))
            except:
                numeric_value = 1.0  # fallback
            generic_goals.append({"Title": title, "TargetValue": numeric_value})

    return pd.DataFrame(generic_goals)


def get_weekly_goals(user_id):
    PROJECT_ID = "vivianaramos6techx25"
    DATASET_ID = "ISE"
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT Title, TargetValue, CurrentValue
        FROM ISE.PersonalGoals
        WHERE UserId = '{user_id}' AND StartDate >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    """
    return client.query(query).to_dataframe()

def mark_goal_as_completed(user_id, title):
    from google.cloud import bigquery
    client = bigquery.Client(project="vivianaramos6techx25")
    
    update_query = f"""
        UPDATE ISE.PersonalGoals
        SET IsCompleted = TRUE
        WHERE UserId = '{user_id}' AND Title = '{title}'
    """
    client.query(update_query)


def get_completed_goals(user_id):
    PROJECT_ID = "vivianaramos6techx25"
    DATASET_ID = "ISE"
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT Title, TargetValue, StartDate, EndDate
        FROM ISE.PersonalGoals
        WHERE UserId = '{user_id}' AND IsCompleted = TRUE
    """
    return client.query(query).to_dataframe()

def get_user_achievements(user_id):
    from google.cloud import bigquery
    client = bigquery.Client(project="vivianaramos6techx25")

    query = f"""
        SELECT a.Name, a.Description, ua.EarnedDate
        FROM ISE.UserAchievements ua
        JOIN ISE.Achievements a ON ua.AchievementId = a.AchievementId
        WHERE ua.UserId = '{user_id}'
        ORDER BY ua.EarnedDate
    """
    df = client.query(query).to_dataframe()
    
    # Optional: Add emojis or formatted labels if you're using this in Streamlit
    df["Name"] = df["Name"].apply(lambda n: f"🏆 {n}")
    return df


def get_group_goals(user_id):
    from google.cloud import bigquery
    import pandas as pd
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    import vertexai

    # Initialize Vertex AI if not already done in your project setup
    vertexai.init(project="vivianaramos6techx25", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")
    
    client = bigquery.Client(project="vivianaramos6techx25")

    # Step 1: Get all groups where the user is a member
    group_query = f"""
        SELECT g.GroupId, g.Name, g.Category
        FROM ISE.GroupMemberships m
        JOIN ISE.FitnessGroups g ON m.GroupId = g.GroupId
        WHERE m.UserId = '{user_id}'
    """
    groups = client.query(group_query).to_dataframe()

    if groups.empty:
        # Return an empty DataFrame if the user is not in any group
        return pd.DataFrame(columns=["Description", "Contribution", "TargetValue", "RewardClaimed", "GroupId", "GroupName"])

    group_goals = []
    # Step 2: For each group, generate a specific weekly goal using Gemini
    for _, row in groups.iterrows():
        group_name = row["Name"]
        category = row["Category"]
        group_id = row["GroupId"]

        # Construct a detailed prompt to get a measurable goal for the group
        prompt = (
            f"You are a fitness coach. Create a short, weekly fitness goal "
            f"for someone in a {category} group called '{group_name}'. "
            "The goal should be specific, measurable, and no more than 10 words. "
            "Example: 'Run 3 miles, 3 times this week.' "
            "Now, generate a goal for this group:"
        )

        
        # Generate the goal from the model
        response = model.generate_content(prompt)
        description = response.text.strip()

        # If no result is returned, use a fallback message
        if not description:
            description = f"Participate actively in {group_name} activities this week."

        group_goals.append({
            "Description": description,
            "Contribution": 0,   # Default value; this could later be updated with actual progress data
            "TargetValue": 1.0,  # Placeholder target value for display; update as needed
            "RewardClaimed": False,
            "GroupId": group_id,
            "GroupName": group_name
        })

    return pd.DataFrame(group_goals)



def check_and_award_goal_achievements(user_id):
    from google.cloud import bigquery
    from datetime import date

    client = bigquery.Client(project="vivianaramos6techx25")

    # Count completed personal goals
    count_query = f"""
        SELECT COUNT(*) as completed_count
        FROM ISE.PersonalGoals
        WHERE UserId = '{user_id}' AND IsCompleted = TRUE
    """
    completed_count = client.query(count_query).to_dataframe().iloc[0]["completed_count"]

    # Get existing achievements
    existing_query = f"""
        SELECT AchievementId FROM ISE.UserAchievements WHERE UserId = '{user_id}'
    """
    existing_achievements = set(client.query(existing_query).to_dataframe()["AchievementId"])

    # Define structured goal achievements
    GOAL_ACHIEVEMENTS = [
        {"id": "goal_ach1", "threshold": 5, "name": "Bronze Finisher", "description": "Completed 5 personal goals"},
        {"id": "goal_ach2", "threshold": 10, "name": "Silver Achiever", "description": "Completed 10 personal goals"},
        {"id": "goal_ach3", "threshold": 20, "name": "Gold Master", "description": "Completed 20 personal goals"},
    ]

    # Loop through and award any new ones
    for ach in GOAL_ACHIEVEMENTS:
        if completed_count >= ach["threshold"] and ach["id"] not in existing_achievements:
            insert_query = f"""
                INSERT INTO ISE.UserAchievements (UserId, AchievementId, EarnedDate)
                VALUES ('{user_id}', '{ach['id']}', CURRENT_DATE())
            """
            client.query(insert_query)


def add_suggested_goal_to_weekly(user_id, title, target_value):
    client = bigquery.Client()
    goal_id = f"pg_{uuid.uuid4().hex[:6]}"
    today = date.today()
    end_date = today + timedelta(days=7)

    query = f"""
        INSERT INTO `vivianaramos6techx25.ISE.PersonalGoals`
        (GoalId, UserId, Title, Description, TargetValue, CurrentValue, StartDate, EndDate, IsCompleted, IsCustom)
        VALUES (
            '{goal_id}',
            '{user_id}',
            '{title}',
            NULL,
            {target_value},
            0,
            '{today}',
            '{end_date}',
            FALSE,
            FALSE
        )
    """
    client.query(query).result()

def add_group_goal_to_weekly(user_id, title, target_value):
    client = bigquery.Client()
    goal_id = f"pg_{uuid.uuid4().hex[:6]}"
    today = date.today()
    end_date = today + timedelta(days=7)

    query = f"""
        INSERT INTO `vivianaramos6techx25.ISE.PersonalGoals`
        (GoalId, UserId, Title, Description, TargetValue, CurrentValue, StartDate, EndDate, IsCompleted, IsCustom)
        VALUES (
            '{goal_id}',
            '{user_id}',
            '{title}',
            NULL,
            {target_value},
            0,
            '{today}',
            '{end_date}',
            FALSE,
            TRUE
        )
    """
    client.query(query).result()
