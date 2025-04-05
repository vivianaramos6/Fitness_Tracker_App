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

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}


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
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


def get_user_posts(user_id):
    """Returns a list of a user's posts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'image_url',
    }]


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
    