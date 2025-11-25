#!/usr/bin/env python3
"""
Debug script to test search functionality
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from youtube_downloader import YouTubeDownloader

def test_search():
    """Test search functionality with debug output"""
    print("Testing search functionality...")
    
    try:
        downloader = YouTubeDownloader()
        
        # Enable debug logging
        import logging
        logging.getLogger('youtube_downloader').setLevel(logging.DEBUG)
        
        print("Searching for 'python tutorial'...")
        videos = downloader.search_videos("python tutorial", max_results=3)
        
        print(f"Found {len(videos)} videos")
        
        if videos:
            for i, video in enumerate(videos, 1):
                print(f"\n{i}. {video['title']}")
                print(f"   URL: {video['url']}")
                print(f"   Duration: {video['duration']}")
                print(f"   Channel: {video['channel']}")
        else:
            print("No videos found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()