#!/usr/bin/env python3
"""
YouTube Downloader Automation
Core downloader class for searching and downloading YouTube videos.
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import re
from datetime import datetime

import yt_dlp
# from youtubesearchpython import VideosSearch  # Commented out due to compatibility issues
from rich.console import Console
from rich.progress import (
    Progress, 
    TaskID, 
    BarColumn, 
    TextColumn, 
    TimeRemainingColumn,
    DownloadColumn,
    TransferSpeedColumn
)
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Import AI helper
try:
    from .ai_helper import AIHelper
except ImportError:
    from ai_helper import AIHelper

class YouTubeDownloader:
    """
    Main class for YouTube video search and download functionality.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.console = Console()
        self.config = self._load_config(config_file)
        self.setup_logging()
        
        # Create downloads directory if it doesn't exist
        self.downloads_dir = Path(self.config.get('downloads_dir', 'downloads'))
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Store downloaded video info
        self.downloaded_videos = []
        
        # Load existing download history
        self.download_history = self._load_download_history()
        
        # Initialize AI helper
        self.ai_helper = AIHelper(self.config)
        if self.ai_helper.is_enabled():
            rprint("[green]🤖 AI-powered search enhancement enabled[/green]")
            self.logger.info("🤖 AI-powered search enhancement enabled")
        
    def _load_config(self, config_file: str = None) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_file (str): Path to config file
            
        Returns:
            Dict: Configuration dictionary
        """
        default_config = {
            'downloads_dir': 'downloads',
            'video_quality': 'best[height<=720]',
            'audio_quality': 'best',
            'output_format': 'mp4',
            'max_duration': 1800,  # 30 minutes
            'concurrent_downloads': 3,
            'log_level': 'INFO',
            'ai_enabled': False,  # AI disabled by default if no config
        }
        
        # Default to config/config.yaml if no config file specified
        if not config_file:
            default_path = Path('config/config.yaml')
            if default_path.exists():
                config_file = str(default_path)
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    import yaml
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                
        return default_config
    
    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'youtube_downloader_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def search_videos(self, query: str, max_results: int = 10, skip_downloaded: bool = True) -> List[Dict]:
        """
        Search for videos on YouTube with AI-enhanced search and filtering.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            skip_downloaded (bool): Whether to filter out already downloaded videos
            
        Returns:
            List[Dict]: List of video information dictionaries
        """
        try:
            self.logger.info(f"Searching for videos: '{query}' (max: {max_results})")
            
            # Get AI search intent if enabled
            search_intent = None
            enhanced_query = query
            if self.ai_helper.is_enabled():
                search_intent = self.ai_helper.get_search_intent_and_criteria(query)
                enhanced_query = search_intent.get('keywords', query)
            
            # Search for more videos initially to account for duplicates and AI filtering
            search_multiplier = 5 if self.ai_helper.is_enabled() else (3 if skip_downloaded else 1)
            initial_search_count = max_results * search_multiplier
            
            # Use yt-dlp as the search method (most reliable)
            all_videos = self._search_with_yt_dlp(enhanced_query, initial_search_count)
            
            # Use AI to filter and rank results if enabled
            if self.ai_helper.is_enabled() and all_videos:
                rprint("[cyan]🤖 AI is analyzing videos to find the best matches...[/cyan]")
                self.logger.info("🤖 AI analyzing and ranking search results...")
                all_videos = self.ai_helper.filter_and_rank_results(query, all_videos, len(all_videos), search_intent)
            
            if skip_downloaded and all_videos:
                # Filter out already downloaded videos
                new_videos, already_downloaded = self.filter_already_downloaded(all_videos)
                
                if already_downloaded:
                    self.display_duplicate_summary(already_downloaded)
                
                # Take only the requested number of new videos
                videos = new_videos[:max_results]
                
                self.logger.info(f"Found {len(all_videos)} total videos, {len(already_downloaded)} already downloaded, returning {len(videos)} new videos")
            else:
                videos = all_videos[:max_results]
                self.logger.info(f"Found {len(videos)} suitable videos")
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Error in search_videos: {e}")
            return []
    
    def _search_with_youtube_search_python(self, query: str, max_results: int) -> List[Dict]:
        """
        Search using youtube-search-python library (fallback method).
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            List[Dict]: List of video information dictionaries
        """
        try:
            # Import here to handle missing dependency gracefully
            from youtubesearchpython import VideosSearch
            
            # Use a more conservative approach to avoid the proxies issue
            videos_search = VideosSearch(query, limit=max_results)
            
            # Get results without additional parameters
            results = videos_search.result()
            
            if not results or 'result' not in results:
                self.logger.warning("No search results found with youtube-search-python")
                return []
            
            videos = []
            seen_urls = set()  # Track unique URLs to prevent duplicates
            
            for video in results['result']:
                try:
                    # Parse duration safely
                    duration_str = video.get('duration', '0:00')
                    if duration_str is None:
                        duration_str = '0:00'
                    
                    duration_seconds = self._parse_duration(duration_str)
                    
                    # Skip videos longer than max_duration
                    if duration_seconds > self.config.get('max_duration', 1800):
                        self.logger.info(f"Skipping video '{video.get('title', 'Unknown')}' - too long ({duration_str})")
                        continue
                    
                    video_url = video.get('link', '')
                    
                    # Skip duplicate URLs in the same search result
                    if video_url in seen_urls:
                        self.logger.debug(f"Skipping duplicate URL in search results: {video_url}")
                        continue
                    
                    # Safely extract video information
                    thumbnail = self._safe_get_thumbnail(video)
                    if not thumbnail:
                        # Extract video ID and use YouTube's thumbnail URL
                        video_id = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else ''
                        if video_id:
                            thumbnail = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                    
                    video_info = {
                        'title': video.get('title', 'Unknown Title'),
                        'url': video_url,
                        'duration': duration_str,
                        'duration_seconds': duration_seconds,
                        'views': self._safe_get_views(video),
                        'channel': self._safe_get_channel(video),
                        'thumbnail': thumbnail,
                        'published': video.get('publishedTime', 'Unknown')
                    }
                    
                    # Only add videos with valid URLs
                    if video_info['url']:
                        videos.append(video_info)
                        seen_urls.add(video_url)  # Mark this URL as seen
                        
                except Exception as video_error:
                    self.logger.warning(f"Error processing video result: {video_error}")
                    continue
            
            self.logger.info(f"Returning {len(videos)} unique videos from search")
            return videos
            
        except ImportError:
            self.logger.warning("youtube-search-python not available")
            return []
        except Exception as e:
            self.logger.warning(f"youtube-search-python failed: {e}")
            return []
    
    def _search_with_yt_dlp(self, query: str, max_results: int) -> List[Dict]:
        """
        Alternative search using yt-dlp's search capabilities.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            List[Dict]: List of video information dictionaries
        """
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for videos
                search_query = f"ytsearch{max_results}:{query}"
                search_results = ydl.extract_info(search_query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    self.logger.debug("No search results or entries found")
                    return []
                
                self.logger.debug(f"Processing {len(search_results['entries'])} search results")
                
                videos = []
                seen_urls = set()  # Track unique URLs to prevent duplicates
                
                for i, entry in enumerate(search_results['entries'][:max_results]):
                    if not entry:
                        self.logger.debug(f"Entry {i} is None, skipping")
                        continue
                    
                    try:
                        self.logger.debug(f"Processing entry {i}: {entry.get('title', 'Unknown')}")
                        
                        # Get basic info from search results
                        duration_seconds = entry.get('duration', 0) or 0
                        
                        # Handle duration if it's a float
                        if isinstance(duration_seconds, float):
                            duration_seconds = int(duration_seconds)
                        elif not isinstance(duration_seconds, int):
                            duration_seconds = 0
                        
                        self.logger.debug(f"Video duration: {duration_seconds}s, max allowed: {self.config.get('max_duration', 1800)}s")
                        
                        # Skip very long videos
                        if duration_seconds > self.config.get('max_duration', 1800):
                            self.logger.debug(f"Skipping video - too long: {duration_seconds}s")
                            continue
                        
                        # Safely format view count
                        view_count = entry.get('view_count', 0)
                        if view_count is None:
                            view_count_str = '0'
                        elif isinstance(view_count, (int, float)):
                            view_count_str = str(int(view_count))
                        else:
                            view_count_str = str(view_count)
                        
                        video_id = entry.get('id', '')
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Skip duplicate URLs in the same search result
                        if video_url in seen_urls:
                            self.logger.debug(f"Skipping duplicate URL in search results: {video_url}")
                            continue
                        
                        # Get thumbnail URL with multiple fallbacks
                        thumbnail_url = entry.get('thumbnail', '')
                        
                        # Try thumbnails array if main thumbnail is empty
                        if not thumbnail_url:
                            thumbnails = entry.get('thumbnails', [])
                            if thumbnails and isinstance(thumbnails, list) and len(thumbnails) > 0:
                                # Get the highest quality thumbnail (usually last in list)
                                thumbnail_url = thumbnails[-1].get('url', '')
                        
                        # Final fallback to YouTube's default thumbnail format
                        if not thumbnail_url and video_id:
                            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                        
                        # If still no thumbnail, use standard quality fallback
                        if not thumbnail_url and video_id:
                            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                        
                        video_info = {
                            'title': entry.get('title', 'Unknown Title'),
                            'url': video_url,
                            'duration': self._format_duration_from_seconds(duration_seconds),
                            'duration_seconds': duration_seconds,
                            'views': view_count_str,
                            'channel': entry.get('uploader', 'Unknown Channel'),
                            'thumbnail': thumbnail_url,
                            'published': entry.get('upload_date', 'Unknown')
                        }
                        
                        if video_info['url'] and 'v=' in video_info['url']:
                            videos.append(video_info)
                            seen_urls.add(video_url)  # Mark this URL as seen
                            self.logger.debug(f"Added video: {video_info['title']}")
                        else:
                            self.logger.debug(f"Skipping video - invalid URL: {video_info['url']}")
                            
                    except Exception as video_error:
                        self.logger.warning(f"Error processing yt-dlp result: {video_error}")
                        continue
                
                self.logger.info(f"Returning {len(videos)} unique videos from search (filtered {len(seen_urls) - len(videos)} duplicates)")
                return videos
                
        except Exception as e:
            self.logger.warning(f"yt-dlp search failed: {e}")
            return []
    
    def _safe_get_views(self, video: dict) -> str:
        """Safely extract view count from video data."""
        try:
            view_count = video.get('viewCount', {})
            if isinstance(view_count, dict):
                return view_count.get('text', '0')
            return str(view_count) if view_count else '0'
        except:
            return '0'
    
    def _safe_get_channel(self, video: dict) -> str:
        """Safely extract channel name from video data."""
        try:
            channel = video.get('channel', {})
            if isinstance(channel, dict):
                return channel.get('name', 'Unknown Channel')
            return str(channel) if channel else 'Unknown Channel'
        except:
            return 'Unknown Channel'
    
    def _safe_get_thumbnail(self, video: dict) -> str:
        """Safely extract thumbnail URL from video data with fallbacks."""
        try:
            # Try to get from thumbnails array (highest quality, usually last)
            thumbnails = video.get('thumbnails', [])
            if thumbnails and isinstance(thumbnails, list) and len(thumbnails) > 0:
                # Get highest quality (last in array)
                thumbnail_url = thumbnails[-1].get('url', '')
                if thumbnail_url:
                    return thumbnail_url
            
            # Try direct thumbnail field
            thumbnail = video.get('thumbnail', '')
            if thumbnail:
                return thumbnail
            
            # Fallback: Extract video ID and construct YouTube thumbnail URL
            video_url = video.get('link', '')
            if video_url and 'v=' in video_url:
                video_id = video_url.split('v=')[-1].split('&')[0]
                if video_id:
                    return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            
            return ''
        except Exception as e:
            self.logger.debug(f"Error extracting thumbnail: {e}")
            return ''
    
    def _format_duration_from_seconds(self, seconds: int) -> str:
        """
        Format duration from seconds to MM:SS or HH:MM:SS format.
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration string
        """
        if seconds <= 0:
            return '0:00'
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse duration string to seconds.
        
        Args:
            duration_str (str): Duration in format "MM:SS" or "HH:MM:SS"
            
        Returns:
            int: Duration in seconds
        """
        try:
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
    
    def display_search_results(self, videos: List[Dict]):
        """
        Display search results in a formatted table.
        
        Args:
            videos (List[Dict]): List of video information
        """
        if not videos:
            rprint("[yellow]No videos found matching your criteria.[/yellow]")
            return
        
        table = Table(title="Search Results")
        table.add_column("Index", style="cyan", no_wrap=True)
        table.add_column("Title", style="white", max_width=50)
        table.add_column("Duration", style="green")
        table.add_column("Channel", style="blue", max_width=20)
        table.add_column("Views", style="yellow")
        
        for idx, video in enumerate(videos, 1):
            table.add_row(
                str(idx),
                video['title'][:47] + "..." if len(video['title']) > 50 else video['title'],
                video['duration'],
                video['channel'][:17] + "..." if len(video['channel']) > 20 else video['channel'],
                video['views']
            )
        
        self.console.print(table)
    
    def download_video(self, video_url: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Download a single video.
        
        Args:
            video_url (str): YouTube video URL
            progress_callback: Callback function for progress updates
            
        Returns:
            Tuple[bool, str]: Success status and file path or error message
        """
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': f"{self.config.get('video_quality', 'best[height<=720]')}+bestaudio[ext=m4a]/best[ext=mp4]/best",
                'outtmpl': str(self.downloads_dir / '%(title)s.%(ext)s'),
                'noplaylist': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': True,
            }
            
            # Add progress hook if callback provided
            if progress_callback:
                ydl_opts['progress_hooks'] = [progress_callback]
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    return False, "Could not extract video information"
                
                # Check duration again
                duration = info.get('duration', 0)
                if duration > self.config.get('max_duration', 1800):
                    return False, f"Video too long: {duration}s (max: {self.config.get('max_duration')}s)"
                
                # Download the video
                ydl.download([video_url])
                
                # Find the downloaded file by checking all files in downloads directory
                downloaded_file = None
                title = info.get('title', 'Unknown')
                
                # Check for files that might match this video
                for file_path in self.downloads_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.webm', '.mkv', '.flv', '.avi']:
                        # Check if this file was created recently (within last minute)
                        file_mtime = file_path.stat().st_mtime
                        current_time = datetime.now().timestamp()
                        
                        if current_time - file_mtime < 120:  # File created in last 2 minutes
                            # This is likely our file
                            downloaded_file = str(file_path)
                            break
                
                # If still not found, try alternative search by title similarity
                if not downloaded_file:
                    sanitized_title = self._sanitize_filename(title)
                    for file_path in self.downloads_dir.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.webm', '.mkv', '.flv', '.avi']:
                            # Check if filename contains parts of the title
                            if any(word.lower() in file_path.name.lower() for word in sanitized_title.split('_')[:3] if len(word) > 3):
                                downloaded_file = str(file_path)
                                break
                
                # If still not found, get the most recent video file
                if not downloaded_file:
                    video_files = [f for f in self.downloads_dir.iterdir() 
                                 if f.is_file() and f.suffix.lower() in ['.mp4', '.webm', '.mkv', '.flv', '.avi']]
                    if video_files:
                        # Get most recently modified file
                        most_recent = max(video_files, key=lambda f: f.stat().st_mtime)
                        downloaded_file = str(most_recent)
                
                if downloaded_file:
                    video_info = {
                        'title': title,
                        'url': video_url,
                        'file_path': downloaded_file,
                        'download_time': datetime.now().isoformat()
                    }
                    
                    # Add to current session downloads
                    self.downloaded_videos.append(video_info)
                    
                    # Add to download history to prevent future duplicates
                    self.download_history[video_url] = video_info
                    
                    return True, downloaded_file
                else:
                    return False, "File downloaded but could not locate it"
                
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove/replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
        return filename[:100]  # Limit length
    
    def _load_download_history(self) -> Dict:
        """
        Load download history from existing files.
        
        Returns:
            Dict: Dictionary with URLs as keys and video info as values
        """
        history = {}
        
        try:
            # Look for existing download history files
            history_files = list(self.downloads_dir.glob('download_history_*.json'))
            
            for history_file in history_files:
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        file_history = json.load(f)
                        
                    # Convert list to dictionary for faster lookup
                    if isinstance(file_history, list):
                        for video in file_history:
                            if 'url' in video:
                                history[video['url']] = video
                    elif isinstance(file_history, dict):
                        history.update(file_history)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.warning(f"Error loading history file {history_file}: {e}")
                    continue
            
            self.logger.info(f"Loaded {len(history)} videos from download history")
            
        except Exception as e:
            self.logger.warning(f"Error loading download history: {e}")
        
        return history
    
    def _is_already_downloaded(self, video_url: str) -> bool:
        """
        Check if a video has already been downloaded.
        
        Args:
            video_url (str): Video URL to check
            
        Returns:
            bool: True if video was already downloaded
        """
        return video_url in self.download_history
    
    def _get_downloaded_video_info(self, video_url: str) -> Optional[Dict]:
        """
        Get information about a previously downloaded video.
        
        Args:
            video_url (str): Video URL to look up
            
        Returns:
            Optional[Dict]: Video information if found, None otherwise
        """
        return self.download_history.get(video_url)
    
    def filter_already_downloaded(self, videos: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter out videos that have already been downloaded.
        
        Args:
            videos (List[Dict]): List of video information
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (new_videos, already_downloaded_videos)
        """
        new_videos = []
        already_downloaded = []
        
        for video in videos:
            video_url = video.get('url', '')
            if self._is_already_downloaded(video_url):
                # Add info about when it was downloaded
                downloaded_info = self._get_downloaded_video_info(video_url)
                video['previously_downloaded'] = downloaded_info.get('download_time', 'Unknown')
                video['previous_file'] = downloaded_info.get('file_path', 'Unknown')
                already_downloaded.append(video)
            else:
                new_videos.append(video)
        
        return new_videos, already_downloaded
    
    def display_duplicate_summary(self, already_downloaded: List[Dict]):
        """
        Display a summary of videos that were skipped because they're already downloaded.
        
        Args:
            already_downloaded (List[Dict]): List of already downloaded videos
        """
        if not already_downloaded:
            return
        
        rprint(f"\n[yellow]Skipped {len(already_downloaded)} video(s) already in download history:[/yellow]")
        
        for video in already_downloaded[:5]:  # Show first 5
            title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
            download_time = video.get('previously_downloaded', 'Unknown')
            
            # Format download time if it's an ISO string
            try:
                if download_time != 'Unknown' and 'T' in download_time:
                    dt = datetime.fromisoformat(download_time.replace('Z', '+00:00'))
                    download_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
                
            rprint(f"  • {title} (downloaded: {download_time})")
        
        if len(already_downloaded) > 5:
            rprint(f"  ... and {len(already_downloaded) - 5} more")
    
    def download_multiple_videos(self, video_urls: List[str]) -> Dict:
        """
        Download multiple videos with progress tracking.
        
        Args:
            video_urls (List[str]): List of YouTube video URLs
            
        Returns:
            Dict: Download results summary
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(video_urls)
        }
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TransferSpeedColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task(
                f"Downloading {len(video_urls)} videos...", 
                total=len(video_urls)
            )
            
            for idx, url in enumerate(video_urls, 1):
                current_task = progress.add_task(
                    f"Video {idx}/{len(video_urls)}", 
                    total=100
                )
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d and d['total_bytes']:
                            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            progress.update(current_task, completed=percent)
                        elif '_percent_str' in d:
                            percent_str = d['_percent_str'].strip('%')
                            try:
                                percent = float(percent_str)
                                progress.update(current_task, completed=percent)
                            except ValueError:
                                pass
                
                success, result = self.download_video(url, progress_hook)
                
                if success:
                    results['successful'].append({'url': url, 'file': result})
                    self.logger.info(f"Downloaded: {result}")
                else:
                    results['failed'].append({'url': url, 'error': result})
                    self.logger.error(f"Failed to download {url}: {result}")
                
                progress.update(current_task, completed=100)
                progress.update(main_task, advance=1)
        
        return results
    
    def save_download_history(self, filename: str = None):
        """
        Save download history to JSON file.
        
        Args:
            filename (str): Output filename (optional)
        """
        if not filename:
            filename = f"download_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        history_file = self.downloads_dir / filename
        
        try:
            with open(history_file, 'w') as f:
                json.dump(self.downloaded_videos, f, indent=2)
            
            self.logger.info(f"Download history saved to {history_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save download history: {e}")
    
    def get_download_summary(self) -> Dict:
        """
        Get summary of downloads.
        
        Returns:
            Dict: Download summary statistics
        """
        total_files = len(self.downloaded_videos)
        total_size = 0
        
        for video in self.downloaded_videos:
            file_path = video.get('file_path', '')
            if file_path and os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        return {
            'total_downloads': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'downloads_dir': str(self.downloads_dir),
            'history_count': len(self.download_history)
        }
    
    def get_download_history_stats(self) -> Dict:
        """
        Get statistics about download history.
        
        Returns:
            Dict: Download history statistics
        """
        if not self.download_history:
            return {
                'total_videos': 0,
                'oldest_download': None,
                'newest_download': None,
                'total_size_mb': 0
            }
        
        # Calculate stats
        download_times = []
        total_size = 0
        
        for video_info in self.download_history.values():
            # Parse download time
            download_time = video_info.get('download_time')
            if download_time:
                try:
                    dt = datetime.fromisoformat(download_time.replace('Z', '+00:00'))
                    download_times.append(dt)
                except:
                    pass
            
            # Calculate file size if file exists
            file_path = video_info.get('file_path', '')
            if file_path and os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        oldest = min(download_times) if download_times else None
        newest = max(download_times) if download_times else None
        
        return {
            'total_videos': len(self.download_history),
            'oldest_download': oldest.strftime('%Y-%m-%d %H:%M') if oldest else None,
            'newest_download': newest.strftime('%Y-%m-%d %H:%M') if newest else None,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }


if __name__ == "__main__":
    # Simple test
    downloader = YouTubeDownloader()
    videos = downloader.search_videos("funny cats", 3)
    downloader.display_search_results(videos)