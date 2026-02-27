from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone


load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

youtube_client = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

def get_uploads_playlist_id(channel_id):
    request = youtube_client.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_videos_from_playlist(playlist_id, max_results=20, hours_back=24):
    videos = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

    
    request = youtube_client.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    for item in response["items"]:
        published_at = datetime.fromisoformat(
            item["snippet"]["publishedAt"].replace("Z", "+00:00")
        )

        if published_at < cutoff_time:
            break

        print(item["snippet"]["title"])
        video_data = {
            "video_id": item["snippet"]["resourceId"]["videoId"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "published_at": item["snippet"]["publishedAt"],
            "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
        }
        videos.append(video_data)

    return videos

CHANNEL_ID = "UCawZsQWqfGSbCI5yjkdVkTA"  # example channel ID

uploads_playlist_id = get_uploads_playlist_id(CHANNEL_ID)
videos = get_videos_from_playlist(uploads_playlist_id)
print(videos)

