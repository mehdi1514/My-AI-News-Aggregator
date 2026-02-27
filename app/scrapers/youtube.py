from datetime import datetime, timedelta, timezone
from typing import List, Optional
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()


class Transcript(BaseModel):
    text: str


class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None


class YouTubeScraper:
    def __init__(self):
        proxy_config = None
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")
        
        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password
            )
        
        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        self.youtube_client = build(
            "youtube",
            "v3",
            developerKey=os.getenv("GOOGLE_API_KEY")
        )

    def _get_uploads_playlist_id(self, channel_id: str) -> str:
        request = self.youtube_client.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        if not response.get("items"):
            raise ValueError(f"Channel {channel_id} not found")
        return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        try:
            transcript = self.transcript_api.fetch(video_id)
            text = " ".join([snippet.text for snippet in transcript.snippets])
            return Transcript(text=text)
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        try:
            uploads_playlist_id = self._get_uploads_playlist_id(channel_id)
        except Exception as e:
            print(f"Error getting playlist ID: {e}")
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []
        
        request = self.youtube_client.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50
        )
        
        while request:
            response = request.execute()
            
            for item in response.get("items", []):
                published_at_str = item["snippet"]["publishedAt"]
                published_time = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                
                if published_time < cutoff_time:
                    return videos

                video_id = item["snippet"]["resourceId"]["videoId"]
                videos.append(ChannelVideo(
                    title=item["snippet"]["title"],
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    video_id=video_id,
                    published_at=published_time,
                    description=item["snippet"]["description"]
                ))
            
            request = self.youtube_client.playlistItems().list_next(request, response)
        
        return videos

    def scrape_channel(self, channel_id: str, hours: int = 150) -> list[ChannelVideo]:
        videos = self.get_latest_videos(channel_id, hours)
        result = []
        for video in videos:
            try:
                transcript: Transcript = self.get_transcript(video.video_id)
                result.append(video.model_copy(update={"transcript": transcript.text if transcript else None}))
            except Exception as e:
                print(f"Error getting transcript for video {video.video_id}: {e}")
                result.append(video.model_copy(update={"transcript": None}))
        return result
    
    
    
if __name__ == "__main__":
    scraper = YouTubeScraper()
    # transcript: Transcript = scraper.get_transcript("jqd6_bbjhS8")
    # print(transcript.text)
    channel_videos: List[ChannelVideo] = scraper.scrape_channel("UCawZsQWqfGSbCI5yjkdVkTA", hours=24)
    print(channel_videos)

    
