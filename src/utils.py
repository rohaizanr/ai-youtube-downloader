#!/usr/bin/env python3
"""
Utility functions for YouTube Downloader Automation
Common helper functions and error handling utilities.
"""

import os
import re
import logging
import sys
from typing import Optional, Tuple, List
from pathlib import Path
import json
from datetime import datetime

class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration with both file and console handlers.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str): Path to log file (optional)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename if not provided
    if not log_file:
        log_file = log_dir / f'youtube_downloader_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Create logger
    logger = logging.getLogger('youtube_downloader')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (only for WARNING and above to avoid cluttering output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid YouTube URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid YouTube URL
    """
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    
    return False

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename for filesystem compatibility.
    
    Args:
        filename (str): Original filename
        max_length (int): Maximum length for filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove/replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = re.sub(r'_+', '_', filename)   # Replace multiple underscores with single
    filename = filename.strip('_')            # Remove leading/trailing underscores
    
    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "1:23:45" or "5:30")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to seconds.
    
    Args:
        duration_str (str): Duration in format "MM:SS" or "HH:MM:SS"
        
    Returns:
        int: Duration in seconds
    """
    try:
        # Handle different formats
        if duration_str.lower() in ['live', 'streaming', '']:
            return 0
        
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            return 0
    except (ValueError, AttributeError):
        return 0

def format_size(bytes_size: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        bytes_size (int): Size in bytes
        
    Returns:
        str: Formatted size (e.g., "1.5 GB", "256 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format (alias for format_size).
    
    Args:
        size_bytes (int): File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    return format_size(size_bytes)

def get_video_thumbnail(video_url: str) -> Optional[str]:
    """
    Extract YouTube video thumbnail URL from video URL.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        Optional[str]: Thumbnail URL or None
    """
    # Extract video ID from URL
    video_id = extract_video_id(video_url)
    
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    
    return None

def extract_video_id(video_url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        Optional[str]: Video ID or None
    """
    # Handle various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
        r'youtube\.com\/embed\/([^&\n?]*)',
        r'youtube\.com\/v\/([^&\n?]*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    
    return None

def validate_search_query(query: str) -> Tuple[bool, str]:
    """
    Validate search query input.
    
    Args:
        query (str): Search query to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    
    if len(query.strip()) < 2:
        return False, "Search query must be at least 2 characters long"
    
    if len(query) > 500:
        return False, "Search query is too long (max 500 characters)"
    
    # Check for potentially problematic characters
    problematic_chars = ['<', '>', '"', '\\', '/', '|']
    if any(char in query for char in problematic_chars):
        return False, "Search query contains invalid characters"
    
    return True, ""

def validate_download_count(count: int) -> Tuple[bool, str]:
    """
    Validate number of videos to download.
    
    Args:
        count (int): Number of videos
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if count <= 0:
        return False, "Number of videos must be greater than 0"
    
    if count > 100:
        return False, "Too many videos requested (max 100)"
    
    return True, ""

def create_directory_safe(path: str) -> bool:
    """
    Safely create directory with error handling.
    
    Args:
        path (str): Directory path to create
        
    Returns:
        bool: True if successful
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False

def get_free_disk_space(path: str) -> int:
    """
    Get free disk space in bytes for given path.
    
    Args:
        path (str): Path to check
        
    Returns:
        int: Free space in bytes
    """
    try:
        statvfs = os.statvfs(path)
        return statvfs.f_frsize * statvfs.f_bavail
    except (OSError, AttributeError):
        return 0

def save_json_safe(data: dict, filepath: str) -> bool:
    """
    Safely save data to JSON file with error handling.
    
    Args:
        data (dict): Data to save
        filepath (str): Path to save file
        
    Returns:
        bool: True if successful
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (OSError, PermissionError, json.JSONEncodeError) as e:
        logging.error(f"Failed to save JSON to {filepath}: {e}")
        return False

def load_json_safe(filepath: str) -> Optional[dict]:
    """
    Safely load data from JSON file with error handling.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        Optional[dict]: Loaded data or None if failed
    """
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, PermissionError, json.JSONDecodeError) as e:
        logging.error(f"Failed to load JSON from {filepath}: {e}")
        return None

def check_system_requirements() -> List[str]:
    """
    Check system requirements and return list of issues.
    
    Returns:
        List[str]: List of requirement issues (empty if all good)
    """
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if ffmpeg is available
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("ffmpeg not found or not working")
    
    # Check write permissions for downloads directory
    downloads_dir = Path('downloads')
    if not create_directory_safe(downloads_dir):
        issues.append("Cannot create/write to downloads directory")
    
    # Check available disk space (warn if less than 1GB)
    free_space = get_free_disk_space('.')
    if free_space < 1024 * 1024 * 1024:  # 1GB
        issues.append(f"Low disk space: {format_size(free_space)} available")
    
    return issues

def handle_keyboard_interrupt(func):
    """
    Decorator to handle keyboard interrupts gracefully.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
    return wrapper

class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        self.print_progress()
    
    def print_progress(self):
        """Print current progress."""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = datetime.now() - self.start_time
            
            # Estimate remaining time
            if self.current > 0:
                rate = self.current / elapsed.total_seconds()
                remaining_items = self.total - self.current
                eta_seconds = remaining_items / rate if rate > 0 else 0
                eta = f" (ETA: {int(eta_seconds)}s)" if eta_seconds < 3600 else ""
            else:
                eta = ""
            
            print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%){eta}", 
                  end='', flush=True)
            
            if self.current >= self.total:
                print()  # New line when complete

if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test validation
    print(f"Valid query test: {validate_search_query('python tutorials')}")
    print(f"Invalid query test: {validate_search_query('')}")
    
    # Test duration parsing
    print(f"Duration parsing: {parse_duration('5:30')} seconds")
    print(f"Duration formatting: {format_duration(330)}")
    
    # Test system requirements
    issues = check_system_requirements()
    if issues:
        print(f"System issues: {issues}")
    else:
        print("System requirements OK")