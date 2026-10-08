# ================================================
# YOUTUBE SERVICE - API INTEGRATION
# ================================================

import os
import pickle
import logging
from typing import Dict, Optional, List
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

logger = logging.getLogger(__name__)

# ================================================
# CONSTANTS
# ================================================

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]
TOKEN_FILE = "token.pkl"


# ================================================
# YOUTUBE SERVICE
# ================================================

class YouTubeService:
    """Handle YouTube API operations."""
    
    def __init__(self, credentials_file: str = "client_secret.json"):
        """Initialize YouTube service."""
        self.credentials_file = credentials_file
        self.service = None
        self.credentials = None
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API."""
        try:
            self.credentials = None
            
            # Load existing token
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Get new credentials if needed
            if not self.credentials or not self.credentials.valid:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                    
                    # Save credentials
                    with open(TOKEN_FILE, 'wb') as token:
                        pickle.dump(self.credentials, token)
                else:
                    logger.error(f"Credentials file {self.credentials_file} not found")
                    return False
            
            # Build service
            self.service = build(
                "youtube",
                "v3",
                credentials=self.credentials
            )
            
            logger.info("✅ YouTube authentication successful")
            return True
        
        except Exception as e:
            logger.error(f"❌ YouTube authentication failed: {e}")
            return False
    
    # =============================================
    # CHANNEL OPERATIONS
    # =============================================
    
    def get_channel_info(self) -> Dict:
        """Get authenticated user's channel information."""
        try:
            if not self.service:
                self.authenticate()
            
            request = self.service.channels().list(
                part="snippet,statistics,brandingSettings",
                mine=True
            )
            
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    "success": True,
                    "channel_id": channel['id'],
                    "channel_name": channel['snippet']['title'],
                    "description": channel['snippet']['description'],
                    "thumbnail_url": channel['snippet']['thumbnails']['default']['url'],
                    "subscriber_count": channel['statistics'].get('subscriberCount', 0),
                    "view_count": channel['statistics'].get('viewCount', 0),
                    "video_count": channel['statistics'].get('videoCount', 0)
                }
            
            return {"success": False, "error": "No channel found"}
        
        except Exception as e:
            logger.error(f"Get channel info error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_channels_list(self) -> Dict:
        """Get list of user's channels."""
        try:
            if not self.service:
                self.authenticate()
            
            request = self.service.channels().list(
                part="snippet,statistics",
                mine=True,
                maxResults=50
            )
            
            response = request.execute()
            channels = []
            
            for channel in response.get('items', []):
                channels.append({
                    "channel_id": channel['id'],
                    "channel_name": channel['snippet']['title'],
                    "subscriber_count": int(channel['statistics'].get('subscriberCount', 0))
                })
            
            return {
                "success": True,
                "channels": channels,
                "total": len(channels)
            }
        
        except Exception as e:
            logger.error(f"Get channels list error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # VIDEO UPLOAD
    # =============================================
    
    def upload_video(self, video_path: str, title: str, description: str,
                    tags: List[str], privacy_status: str = "public",
                    category_id: str = "28") -> Dict:
        """Upload video to YouTube."""
        try:
            if not self.service:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            if not os.path.exists(video_path):
                return {"success": False, "error": f"Video file not found: {video_path}"}
            
            # Prepare request body
            request_body = {
                "snippet": {
                    "title": title[:100],  # Max 100 characters
                    "description": description[:5000],  # Max 5000 characters
                    "tags": tags[:30],  # Max 30 tags
                    "categoryId": category_id,
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en"
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "embeddable": True,
                    "publicStatsViewable": True
                },
                "processingDetails": {
                    "processingStatus": "processing"
                }
            }
            
            # Upload media
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True
            )
            
            request = self.service.videos().insert(
                part="snippet,status,processingDetails",
                body=request_body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            logger.info(f"✅ Video uploaded successfully: {video_id}")
            
            return {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "short_url": f"https://youtu.be/{video_id}"
            }
        
        except Exception as e:
            logger.error(f"❌ Video upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # THUMBNAIL OPERATIONS
    # =============================================
    
    def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> Dict:
        """Upload custom thumbnail for video."""
        try:
            if not self.service:
                self.authenticate()
            
            if not os.path.exists(thumbnail_path):
                return {"success": False, "error": f"Thumbnail file not found: {thumbnail_path}"}
            
            media = MediaFileUpload(
                thumbnail_path,
                mimetype='image/jpeg'
            )
            
            request = self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            
            response = request.execute()
            
            logger.info(f"✅ Thumbnail uploaded for video {video_id}")
            
            return {"success": True, "response": response}
        
        except Exception as e:
            logger.error(f"❌ Thumbnail upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # VIDEO ANALYTICS
    # =============================================
    
    def get_video_stats(self, video_id: str) -> Dict:
        """Get statistics for a specific video."""
        try:
            if not self.service:
                self.authenticate()
            
            request = self.service.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    "success": True,
                    "video_id": video_id,
                    "title": video['snippet']['title'],
                    "view_count": int(video['statistics'].get('viewCount', 0)),
                    "like_count": int(video['statistics'].get('likeCount', 0)),
                    "comment_count": int(video['statistics'].get('commentCount', 0)),
                    "favorite_count": int(video['statistics'].get('favoriteCount', 0))
                }
            
            return {"success": False, "error": "Video not found"}
        
        except Exception as e:
            logger.error(f"Get video stats error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_channel_analytics(self, days: int = 30) -> Dict:
        """Get channel analytics (requires Analytics API)."""
        try:
            # This would require YouTube Analytics API
            # Placeholder for future implementation
            return {
                "success": True,
                "message": "Analytics requires YouTube Analytics API setup",
                "docs": "https://developers.google.com/youtube/analytics/getting-started"
            }
        except Exception as e:
            logger.error(f"Get channel analytics error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # PLAYLIST OPERATIONS
    # =============================================
    
    def create_playlist(self, title: str, description: str = "",
                       privacy: str = "private") -> Dict:
        """Create a new playlist."""
        try:
            if not self.service:
                self.authenticate()
            
            request_body = {
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
            
            request = self.service.playlists().insert(
                part="snippet,status",
                body=request_body
            )
            
            response = request.execute()
            
            logger.info(f"✅ Playlist created: {response['id']}")
            
            return {
                "success": True,
                "playlist_id": response['id'],
                "url": f"https://youtube.com/playlist?list={response['id']}"
            }
        
        except Exception as e:
            logger.error(f"Create playlist error: {e}")
            return {"success": False, "error": str(e)}
    
    def add_to_playlist(self, playlist_id: str, video_id: str) -> Dict:
        """Add video to playlist."""
        try:
            if not self.service:
                self.authenticate()
            
            request_body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            
            request = self.service.playlistItems().insert(
                part="snippet",
                body=request_body
            )
            
            response = request.execute()
            
            logger.info(f"✅ Video added to playlist")
            
            return {"success": True, "item_id": response['id']}
        
        except Exception as e:
            logger.error(f"Add to playlist error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # CAPTIONS OPERATIONS
    # =============================================
    
    def upload_captions(self, video_id: str, caption_file: str,
                       language: str = "en") -> Dict:
        """Upload captions/subtitles to video."""
        try:
            if not self.service:
                self.authenticate()
            
            if not os.path.exists(caption_file):
                return {"success": False, "error": "Caption file not found"}
            
            media = MediaFileUpload(caption_file)
            
            request_body = {
                "snippet": {
                    "videoId": video_id,
                    "language": language,
                    "name": language.upper(),
                    "isDraft": False
                }
            }
            
            request = self.service.captions().insert(
                part="snippet",
                body=request_body,
                media_body=media
            )
            
            response = request.execute()
            
            logger.info(f"✅ Captions uploaded for video {video_id}")
            
            return {"success": True, "caption_id": response['id']}
        
        except Exception as e:
            logger.error(f"Upload captions error: {e}")
            return {"success": False, "error": str(e)}


# ================================================
# SINGLETON INSTANCE
# ================================================

youtube_service = None

def init_youtube_service(credentials_file: str = "client_secret.json") -> YouTubeService:
    """Initialize YouTube service."""
    global youtube_service
    youtube_service = YouTubeService(credentials_file)
    if youtube_service.authenticate():
        return youtube_service
    return None

def get_youtube_service() -> YouTubeService:
    """Get YouTube service instance."""
    if youtube_service is None:
        youtube_service = YouTubeService()
    return youtube_service
