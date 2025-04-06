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
import os
import random

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
    from google.api_core.exceptions import GoogleAPIError

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
    from google.api_core.exceptions import GoogleAPICallError, NotFound, BadRequest
    import logging

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

'''
def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }
'''
def get_genai_advice(user_id):
    """Fetches the advice and image for the given user."""
    
    # Set your project and dataset
    project_id = "vivianaramos6techx25"       # Replace with your actual project ID
    dataset_id = "ISE"      # Replace with your actual dataset name

    client = bigquery.Client(project=project_id)

    # Query to fetch user data
    query = f"""
        SELECT 
            UserId AS user_id,
            Name AS name,
            Username AS username,
            ImageUrl AS image_url
        FROM `{project_id}.{dataset_id}.Users`
        WHERE UserId = @user_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    # Check if any result was returned
    user_data = []
    for row in results:
        user_data.append({
            'user_id': row.user_id,
            'name': row.name,
            'username': row.username,
            'image_url': row.image_url,
        })

    # For simplicity, using random advice and image as placeholders
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])

    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
        'user_data': user_data,
    }