#!/usr/bin/env python3
"""
Usage Examples for YouTube Downloader Automation
Demonstrates various ways to use the application.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Note: This file shows usage examples and requires the virtual environment to be activated

def example_basic_search():
    """Example: Basic video search and display"""
    print("Example 1: Basic Search")
    print("-" * 30)
    
    try:
        from youtube_downloader import YouTubeDownloader
        
        # Initialize downloader
        downloader = YouTubeDownloader()
        
        # Search for videos
        videos = downloader.search_videos("python programming", max_results=5)
        
        # Display results
        downloader.display_search_results(videos)
        
        print(f"Found {len(videos)} videos")
        
    except ImportError:
        print("Error: Please activate the virtual environment first")
        print("Run: source activate_env.sh")

def example_batch_download():
    """Example: Download multiple videos"""
    print("\nExample 2: Batch Download")
    print("-" * 30)
    
    try:
        from youtube_downloader import YouTubeDownloader
        
        # Initialize downloader
        downloader = YouTubeDownloader()
        
        # Search for videos
        videos = downloader.search_videos("short funny videos", max_results=3)
        
        if videos:
            print(f"Found {len(videos)} videos to download:")
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']} ({video['duration']})")
            
            # Get video URLs
            video_urls = [video['url'] for video in videos]
            
            # Download videos (uncomment to actually download)
            # results = downloader.download_multiple_videos(video_urls)
            # print(f"Downloaded {len(results['successful'])} videos successfully")
            
            print("(Download commented out for demo)")
        
    except ImportError:
        print("Error: Please activate the virtual environment first")

def example_custom_config():
    """Example: Using custom configuration"""
    print("\nExample 3: Custom Configuration")
    print("-" * 30)
    
    try:
        from youtube_downloader import YouTubeDownloader
        
        # Initialize with custom config
        downloader = YouTubeDownloader('config/config.yaml')
        
        # Show current configuration
        config = downloader.config
        print("Current configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
    except ImportError:
        print("Error: Please activate the virtual environment first")
    except FileNotFoundError:
        print("Error: Configuration file not found")

def example_search_filtering():
    """Example: Advanced search with filtering"""
    print("\nExample 4: Search Filtering")
    print("-" * 30)
    
    try:
        from youtube_downloader import YouTubeDownloader
        
        # Initialize downloader
        downloader = YouTubeDownloader()
        
        # Search for videos
        all_videos = downloader.search_videos("music videos", max_results=10)
        
        # Filter videos by duration (shorter than 5 minutes)
        short_videos = [v for v in all_videos if v['duration_seconds'] < 300]
        
        print(f"Found {len(all_videos)} total videos")
        print(f"Filtered to {len(short_videos)} videos under 5 minutes")
        
        if short_videos:
            print("\nShort videos:")
            for video in short_videos[:3]:
                print(f"- {video['title']} ({video['duration']})")
        
    except ImportError:
        print("Error: Please activate the virtual environment first")

def example_cli_usage():
    """Example: CLI usage patterns"""
    print("\nExample 5: CLI Usage Patterns")
    print("-" * 30)
    
    examples = [
        "# Interactive mode",
        "python src/main.py",
        "",
        "# Download 5 cat videos",
        "python src/main.py -q 'funny cats' -n 5",
        "",
        "# Download cooking tutorials with custom config",
        "python src/main.py -q 'cooking tutorial' -n 3 -c config/config.yaml",
        "",
        "# Using the convenience script",
        "./run_downloader.sh -q 'python lessons' -n 2",
        "",
        "# Interactive mode with convenience script",
        "./run_downloader.sh"
    ]
    
    for example in examples:
        print(example)

def main():
    """Run all examples"""
    print("YouTube Downloader Automation - Usage Examples")
    print("=" * 50)
    
    print("Note: These examples require the virtual environment to be activated.")
    print("Run: source activate_env.sh\n")
    
    # Run examples
    example_basic_search()
    example_batch_download()
    example_custom_config()
    example_search_filtering()
    example_cli_usage()
    
    print("\n" + "=" * 50)
    print("For more examples, see the README.md file")
    print("To run the application: python src/main.py")

if __name__ == "__main__":
    main()