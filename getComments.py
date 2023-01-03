import google.auth
import re
import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the API key
api_key = 'AIzaSyC9HTVeypthgccdx2mptTnhDJzk0VpjZGY'

# Set up the API client and specify the API key
client = build('youtube', 'v3', developerKey=api_key)

# Set the ID of the video for which you want to retrieve comments
video_id = 'aB4TqT7NSOQ'

# Set the maximum number of comments you want to retrieve
max_results = 1000

comments = []

# Initialize the `page_token` variable to an empty string
page_token = ''

# Set up a loop to retrieve all of the comments for the video
while True:
    # Call the YouTube API to retrieve comments for the video
    results = client.commentThreads().list(
        part='snippet,replies',
        videoId=video_id,
        maxResults=max_results,
        textFormat='plainText',
        pageToken=page_token
    ).execute()

    # Make a request to the YouTube Data API to get the video info
    request = client.videos().list(
        part='snippet',
        id=video_id,
    )
    response = request.execute()

    # Get the video name from the response
    video_name = response['items'][0]['snippet']['title']

    # Store the comments and likes in the list
    for item in results['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']

        # remove all timestamps of any number of digits before and after the colon
        comment = re.sub(r'\d+:\d+', '', comment)

        # Remove punctuation and emojis from the comment
        comment = re.sub(r'[^\w\s]', '', comment)
        comment = re.sub(r'[^\x00-\x7f]', '', comment)

        # Replace newline characters with spaces
        comment = comment.replace('\n', ' ')

        # Collapse multiple spaces into a single space
        comment = re.sub(r'\s+', ' ', comment)

        # All comments are lowercase
        comment = comment.lower()

        # The number of likes for each comment
        likes = item['snippet']['topLevelComment']['snippet']['likeCount']
        comments.append((comment, likes))

    # Check if there are more pages of comments
    if 'nextPageToken' not in results:
        break
    page_token = results['nextPageToken']

# Sort the comments in descending order based on the number of likes
sorted_comments = sorted(comments, key=lambda x: x[1], reverse=True)

with open(f'{video_name}.csv', 'w', newline='') as csvfile:
    # Create a CSV writer
    writer = csv.writer(csvfile)

    # Write the comments to the CSV file
    for comment in sorted_comments:
        writer.writerow([comment[1], comment[0]])
