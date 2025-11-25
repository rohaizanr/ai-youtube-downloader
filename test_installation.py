#!/usr/bin/env python3
"""
Test script for YouTube Downloader Automation
Verifies that all components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import yt_dlp
        print("✓ yt-dlp imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import yt-dlp: {e}")
        return False
    
    try:
        from youtubesearchpython import VideosSearch
        print("✓ youtube-search-python imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import youtube-search-python: {e}")
        return False
    
    try:
        from rich.console import Console
        print("✓ rich imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import rich: {e}")
        return False
    
    try:
        import yaml
        print("✓ PyYAML imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyYAML: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test that custom modules work correctly."""
    print("\nTesting custom modules...")
    
    try:
        from utils import validate_search_query, format_duration, check_system_requirements
        print("✓ utils module imported successfully")
        
        # Test utility functions
        is_valid, msg = validate_search_query("test query")
        if is_valid:
            print("✓ Search query validation works")
        else:
            print(f"✗ Search query validation failed: {msg}")
            return False
        
        duration = format_duration(330)  # 5:30
        if duration == "5:30":
            print("✓ Duration formatting works")
        else:
            print(f"✗ Duration formatting failed: got {duration}, expected 5:30")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import utils: {e}")
        return False
    
    try:
        from youtube_downloader import YouTubeDownloader
        print("✓ YouTubeDownloader imported successfully")
        
        # Test basic initialization
        downloader = YouTubeDownloader()
        print("✓ YouTubeDownloader initialization works")
        
    except ImportError as e:
        print(f"✗ Failed to import YouTubeDownloader: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to initialize YouTubeDownloader: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist."""
    print("\nTesting directories...")
    
    required_dirs = ['downloads', 'logs', 'config']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name} directory exists")
        else:
            print(f"✗ {dir_name} directory missing")
            return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    config_file = 'config/config.yaml'
    if os.path.exists(config_file):
        print(f"✓ Configuration file exists: {config_file}")
        
        try:
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            required_keys = ['downloads_dir', 'video_quality', 'max_duration']
            for key in required_keys:
                if key in config:
                    print(f"✓ Config key '{key}' found")
                else:
                    print(f"✗ Config key '{key}' missing")
                    return False
                    
        except Exception as e:
            print(f"✗ Failed to load configuration: {e}")
            return False
    else:
        print(f"✗ Configuration file missing: {config_file}")
        return False
    
    return True

def test_system_requirements():
    """Test system requirements."""
    print("\nTesting system requirements...")
    
    try:
        from utils import check_system_requirements
        issues = check_system_requirements()
        
        if not issues:
            print("✓ All system requirements met")
            return True
        else:
            print("⚠ System requirement issues:")
            for issue in issues:
                print(f"  • {issue}")
            return True  # Don't fail the test for warnings
            
    except Exception as e:
        print(f"✗ Failed to check system requirements: {e}")
        return False

def test_search_functionality():
    """Test basic search functionality (without downloading)."""
    print("\nTesting search functionality...")
    
    try:
        from youtube_downloader import YouTubeDownloader
        
        downloader = YouTubeDownloader()
        
        # Test search with a simple query
        print("  Performing test search...")
        videos = downloader.search_videos("python tutorial", max_results=3)
        
        if videos and len(videos) > 0:
            print(f"✓ Search returned {len(videos)} results")
            
            # Check if video data has required fields
            first_video = videos[0]
            required_fields = ['title', 'url', 'duration']
            
            for field in required_fields:
                if field in first_video:
                    print(f"✓ Video data contains '{field}'")
                else:
                    print(f"✗ Video data missing '{field}'")
                    return False
            
            return True
        else:
            print("⚠ Search returned no results (this might be normal)")
            return True  # Don't fail for no results
            
    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("YouTube Downloader Automation - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Custom Module Tests", test_custom_modules),
        ("Directory Tests", test_directories),
        ("Configuration Tests", test_config),
        ("System Requirements", test_system_requirements),
        ("Search Functionality", test_search_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<30} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your installation is ready to use.")
        return 0
    else:
        print(f"\n⚠ {failed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())