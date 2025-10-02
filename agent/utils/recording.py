import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import NoCredentialsError
from livekit import api
from livekit.agents import JobContext
import aiohttp

logger = logging.getLogger(__name__)


class RecordingManager:
    """Manages video recording and S3 storage for wedding mirror sessions."""

    def __init__(self, ctx: JobContext, guest_name: str = None):
        self.ctx = ctx
        self.guest_name = guest_name
        self.egress_id = None
        self.recording_url = None
        self.recording_id = None  # Database record ID
        self.filename = None
        
        # Log initialization details
        logger.info(f"RecordingManager initialized for room: {ctx.room.name}")
        logger.info(f"Guest name: {guest_name}")
        
        # Check required environment variables
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_bucket = os.getenv("AWS_BUCKET_NAME")
        aws_region = os.getenv("AWS_REGION")
        
        logger.info(f"AWS credentials available: {bool(aws_key and aws_secret)}")
        logger.info(f"AWS bucket: {aws_bucket}")
        logger.info(f"AWS region: {aws_region}")

    async def start_recording(self) -> Optional[str]:
        """
        Start room recording with S3 storage and immediately save to backend.

        Returns:
            Recording URL, or None if failed
        """
        try:
            # First create the video record in the backend to get the final URL
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/api")
            create_endpoint = f"{backend_url}/videos/simple"
            
            logger.info("Creating video record in backend...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(create_endpoint) as response:
                    if response.status in [200, 201]:
                        record_data = await response.json()
                        self.recording_id = record_data.get("recording_id")
                        self.s3_direct_url = record_data.get("video_url")
                        self.filename = record_data.get("filename")
                        
                        logger.info(f"Video record created - ID: {self.recording_id}, URL: {self.s3_direct_url}")
                    else:
                        response_text = await response.text()
                        logger.error(f"Failed to create video record. Status: {response.status}, Response: {response_text}")
                        return None

            logger.info(f"Starting recording for room: {self.ctx.room.name}")
            logger.info(f"Recording filename: {self.filename}")

            # Configure recording request with the filename from backend
            req = api.RoomCompositeEgressRequest(
                room_name=self.ctx.room.name,
                audio_only=False,
                file_outputs=[
                    api.EncodedFileOutput(
                        file_type=api.EncodedFileType.MP4,
                        filepath=self.filename,
                        s3=api.S3Upload(
                            bucket=os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
                            region=os.getenv("AWS_REGION", "me-central-1"),
                            access_key=os.getenv("AWS_ACCESS_KEY_ID"),
                            secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
                        ),
                    )
                ],
            )

            # Start recording
            lkapi = api.LiveKitAPI()
            res = await lkapi.egress.start_room_composite_egress(req)
            await lkapi.aclose()

            self.egress_id = res.egress_id
            logger.info(f"Recording started with egress ID: {self.egress_id}")

            # Generate presigned URL for immediate access
            self.recording_url = self._generate_presigned_url(self.filename)

            logger.info(f"Recording URLs - Direct: {self.s3_direct_url}, Presigned: {bool(self.recording_url)}")
            
            return self.s3_direct_url

        except Exception as e:
            logger.error(f"Failed to start recording: {e}", exc_info=True)
            
            # Check if it's an egress minutes exceeded error
            if "egress minutes exceeded" in str(e) or "resource_exhausted" in str(e):
                logger.warning("LiveKit egress minutes limit reached - recording unavailable")
            
            return None

    async def stop_recording(self) -> bool:
        """
        Stop the current recording and mark as completed in backend.
        
        Returns:
            True if recording stopped successfully, False otherwise
        """
        if not self.egress_id:
            logger.warning("No active recording to stop")
            return False

        try:
            # Stop LiveKit recording
            lkapi = api.LiveKitAPI()
            await lkapi.egress.stop_egress(self.egress_id)
            await lkapi.aclose()
            
            logger.info(f"Recording stopped for egress ID: {self.egress_id}")
            
            # Mark recording as completed in backend
            if self.recording_id:
                backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/api")
                complete_endpoint = f"{backend_url}/videos/{self.recording_id}/complete"
                
                async with aiohttp.ClientSession() as session:
                    async with session.put(complete_endpoint) as response:
                        if response.status == 200:
                            logger.info("Recording marked as completed in backend")
                        else:
                            response_text = await response.text()
                            logger.warning(f"Failed to mark recording as completed. Status: {response.status}, Response: {response_text}")
            
            return True

        except Exception as e:
            logger.error(f"Failed to stop recording: {e}", exc_info=True)
            return False

    def _generate_presigned_url(self, filepath: str) -> Optional[str]:
        """Generate presigned URL for S3 access."""
        try:
            region = os.getenv("AWS_REGION", "me-central-1")
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=region,
            )

            url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
                    "Key": filepath,
                },
                ExpiresIn=86400 * 7,  # 7 days
            )

            logger.info("Generated presigned URL for recording access")
            return url

        except (NoCredentialsError, Exception) as e:
            logger.warning(f"Could not generate presigned URL: {e}")
            return None



    def get_recording_info(self) -> Dict[str, Any]:
        """Get current recording information."""
        return {
            "egress_id": self.egress_id,
            "recording_url": self.recording_url,
            "s3_direct_url": getattr(self, 's3_direct_url', None),
            "guest_name": self.guest_name,
            "room_name": self.ctx.room.name,
            "is_recording": bool(self.egress_id)
        }
