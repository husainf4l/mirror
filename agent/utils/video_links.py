"""
Video link utility functions for the wedding mirror application.
"""
import os
import boto3
import logging
from botocore.exceptions import NoCredentialsError
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def generate_presigned_url(s3_key: str, expires_in: int = 604800) -> Optional[str]:
    """
    Generate a presigned URL for S3 object access.
    
    Args:
        s3_key: The S3 object key (path within bucket)
        expires_in: URL expiration time in seconds (default: 7 days)
        
    Returns:
        Presigned URL string or None if failed
    """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "me-central-1"),
        )

        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
                "Key": s3_key,
            },
            ExpiresIn=expires_in,
        )

        logger.info(f"Generated presigned URL for S3 key: {s3_key}")
        return url

    except (NoCredentialsError, Exception) as e:
        logger.warning(f"Could not generate presigned URL for {s3_key}: {e}")
        return None


def extract_s3_key_from_url(s3_url: str) -> Optional[str]:
    """
    Extract S3 key from full S3 URL.
    
    Args:
        s3_url: Full S3 URL (e.g., https://bucket.s3.region.amazonaws.com/path/to/file.mp4)
        
    Returns:
        S3 key (path within bucket) or None if parsing fails
    """
    try:
        # Handle different S3 URL formats
        if "amazonaws.com/" in s3_url:
            # Extract everything after the domain/bucket
            parts = s3_url.split("amazonaws.com/")
            if len(parts) > 1:
                return parts[1]
        
        # Handle s3:// protocol
        if s3_url.startswith("s3://"):
            # Format: s3://bucket/key
            parts = s3_url[5:].split("/", 1)
            if len(parts) > 1:
                return parts[1]
                
        logger.warning(f"Could not extract S3 key from URL: {s3_url}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting S3 key from URL {s3_url}: {e}")
        return None


def refresh_presigned_url(existing_url: str, expires_in: int = 604800) -> Optional[str]:
    """
    Refresh an existing presigned URL by extracting the S3 key and generating a new URL.
    
    Args:
        existing_url: Current presigned URL
        expires_in: New URL expiration time in seconds (default: 7 days)
        
    Returns:
        New presigned URL or None if failed
    """
    s3_key = extract_s3_key_from_url(existing_url)
    if not s3_key:
        logger.error(f"Could not extract S3 key from existing URL: {existing_url}")
        return None
        
    return generate_presigned_url(s3_key, expires_in)


def check_s3_object_exists(s3_key: str) -> bool:
    """
    Check if an S3 object exists.
    
    Args:
        s3_key: The S3 object key to check
        
    Returns:
        True if object exists, False otherwise
    """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "me-central-1"),
        )

        s3_client.head_object(
            Bucket=os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
            Key=s3_key
        )
        
        logger.info(f"S3 object exists: {s3_key}")
        return True

    except Exception as e:
        logger.warning(f"S3 object does not exist or error checking: {s3_key} - {e}")
        return False


def get_s3_object_metadata(s3_key: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for an S3 object.
    
    Args:
        s3_key: The S3 object key
        
    Returns:
        Dictionary with metadata or None if failed
    """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "me-central-1"),
        )

        response = s3_client.head_object(
            Bucket=os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
            Key=s3_key
        )
        
        metadata = {
            "content_length": response.get("ContentLength", 0),
            "last_modified": response.get("LastModified"),
            "content_type": response.get("ContentType", ""),
            "etag": response.get("ETag", "").strip('"'),
            "storage_class": response.get("StorageClass", "STANDARD"),
            "metadata": response.get("Metadata", {})
        }
        
        logger.info(f"Retrieved metadata for S3 object: {s3_key}")
        return metadata

    except Exception as e:
        logger.error(f"Error getting S3 object metadata for {s3_key}: {e}")
        return None


def create_video_filename(room_name: str, guest_name: str = None, timestamp: datetime = None) -> str:
    """
    Create a standardized filename for video recordings.
    
    Args:
        room_name: LiveKit room name
        guest_name: Guest name (optional)
        timestamp: Recording timestamp (optional, defaults to now)
        
    Returns:
        Standardized filename string
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    guest_suffix = f"_{guest_name.replace(' ', '_')}" if guest_name else ""
    
    filename = f"recordings/wedding_mirror_{room_name}_{timestamp_str}{guest_suffix}.mp4"
    
    logger.info(f"Created video filename: {filename}")
    return filename


def build_s3_direct_url(s3_key: str) -> str:
    """
    Build a direct S3 URL from an S3 key.
    
    Args:
        s3_key: The S3 object key
        
    Returns:
        Direct S3 URL
    """
    bucket_name = os.getenv("AWS_BUCKET_NAME", "4wk-garage-media")
    region = os.getenv("AWS_REGION", "me-central-1")
    
    url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
    logger.debug(f"Built S3 direct URL: {url}")
    return url
