#!/usr/bin/env python3
"""
YouTube Downloader Automation - Command Line Interface
Interactive CLI for searching and downloading YouTube videos.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from youtube_downloader import YouTubeDownloader


class YouTubeDownloaderCLI:
    """Command Line Interface for YouTube Downloader."""
    
    def __init__(self):
        self.console = Console()
        self.downloader = None
    
    def print_banner(self):
        """Print application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                    YouTube Downloader Automation                     ║
║                     Search & Download YouTube Videos                 ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        rprint("[bold cyan]" + banner + "[/bold cyan]")
    
    def initialize_downloader(self, config_file: Optional[str] = None):
        """Initialize the YouTube downloader."""
        try:
            self.downloader = YouTubeDownloader(config_file)
            rprint("[green]✓ YouTube Downloader initialized successfully![/green]")
        except Exception as e:
            rprint(f"[red]✗ Failed to initialize downloader: {e}[/red]")
            sys.exit(1)
    
    def interactive_mode(self):
        """Run the interactive CLI mode."""
        self.print_banner()
        
        rprint("\n[bold]Welcome to YouTube Downloader Automation![/bold]")
        rprint("This tool helps you search and download YouTube videos based on your queries.\n")
        
        while True:
            try:
                # Get search query from user
                query = Prompt.ask(
                    "[cyan]Enter search query[/cyan]",
                    default="",
                ).strip()
                
                if not query:
                    rprint("[yellow]Please enter a valid search query.[/yellow]")
                    continue
                
                # Get number of videos to download
                max_videos = IntPrompt.ask(
                    "[cyan]How many videos would you like to download?[/cyan]",
                    default=5,
                    show_default=True
                )
                
                # Ask about duplicate handling
                skip_downloaded = Confirm.ask(
                    "[cyan]Skip videos already in download history?[/cyan]",
                    default=True
                )
                
                if max_videos <= 0:
                    rprint("[yellow]Please enter a number greater than 0.[/yellow]")
                    continue
                
                # Search for videos
                search_msg = f"\n[blue]Searching for videos: '{query}'"
                if skip_downloaded:
                    search_msg += " (skipping duplicates)"
                search_msg += "...[/blue]"
                rprint(search_msg)
                videos = self.downloader.search_videos(query, max_videos * 3, skip_downloaded=skip_downloaded)  # Search for more to give options
                
                if not videos:
                    rprint("[yellow]No videos found for your query. Try a different search term.[/yellow]")
                    continue
                
                # Display search results
                self.downloader.display_search_results(videos[:min(len(videos), max_videos * 2)])
                
                # Ask user to select videos or download all
                if len(videos) > max_videos:
                    choice = Prompt.ask(
                        f"\n[cyan]Found {len(videos)} videos. Do you want to:[/cyan]",
                        choices=["all", "select", "top"],
                        default="top"
                    )
                    
                    if choice == "all":
                        selected_videos = videos
                    elif choice == "select":
                        selected_videos = self.select_videos_interactive(videos)
                    else:  # top
                        selected_videos = videos[:max_videos]
                else:
                    selected_videos = videos[:max_videos]
                
                if not selected_videos:
                    rprint("[yellow]No videos selected for download.[/yellow]")
                    continue
                
                # Confirm download
                total_videos = len(selected_videos)
                confirm = Confirm.ask(
                    f"\n[cyan]Download {total_videos} video(s)?[/cyan]",
                    default=True
                )
                
                if not confirm:
                    rprint("[yellow]Download cancelled.[/yellow]")
                    continue
                
                # Download videos
                rprint(f"\n[green]Starting download of {total_videos} videos...[/green]")
                
                video_urls = [video['url'] for video in selected_videos]
                results = self.downloader.download_multiple_videos(video_urls)
                
                # Display results
                self.display_download_results(results)
                
                # Save download history
                self.downloader.save_download_history()
                
                # Ask if user wants to continue
                if not Confirm.ask("\n[cyan]Would you like to search for more videos?[/cyan]", default=False):
                    break
                    
            except KeyboardInterrupt:
                rprint("\n[yellow]Operation cancelled by user.[/yellow]")
                break
            except Exception as e:
                rprint(f"[red]An error occurred: {e}[/red]")
                if not Confirm.ask("[cyan]Would you like to continue?[/cyan]", default=True):
                    break
        
        # Show final summary
        self.show_session_summary()
        rprint("\n[bold green]Thank you for using YouTube Downloader Automation![/bold green]")
    
    def select_videos_interactive(self, videos: List[dict]) -> List[dict]:
        """Allow user to interactively select videos from search results."""
        selected_videos = []
        
        rprint("\n[bold]Select videos to download:[/bold]")
        rprint("[dim]Enter video numbers separated by commas (e.g., 1,3,5) or 'all' for all videos[/dim]")
        
        max_index = len(videos)
        selection = Prompt.ask(
            f"[cyan]Select videos (1-{max_index})[/cyan]",
            default="all"
        ).strip().lower()
        
        if selection == "all":
            return videos
        
        try:
            # Parse selection
            indices = []
            for part in selection.split(','):
                part = part.strip()
                if '-' in part:
                    # Handle ranges like "1-5"
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                else:
                    indices.append(int(part))
            
            # Get selected videos
            for idx in indices:
                if 1 <= idx <= len(videos):
                    selected_videos.append(videos[idx - 1])
                else:
                    rprint(f"[yellow]Warning: Index {idx} is out of range (1-{len(videos)})[/yellow]")
            
        except ValueError:
            rprint("[red]Invalid selection format. Please use numbers separated by commas.[/red]")
            return []
        
        return selected_videos
    
    def display_download_results(self, results: dict):
        """Display download results summary."""
        successful = results.get('successful', [])
        failed = results.get('failed', [])
        total = results.get('total', 0)
        
        # Create summary panel
        summary_text = f"""
[green]✓ Successful downloads: {len(successful)}/{total}[/green]
[red]✗ Failed downloads: {len(failed)}/{total}[/red]
        """
        
        if successful:
            summary_text += "\n[bold]Successfully downloaded:[/bold]\n"
            # Deduplicate filenames in display
            seen_files = set()
            for item in successful:
                filename = Path(item['file']).name
                if filename not in seen_files:
                    summary_text += f"  • {filename}\n"
                    seen_files.add(filename)
        
        if failed:
            summary_text += "\n[bold]Failed downloads:[/bold]\n"
            for item in failed:
                summary_text += f"  • {item['url']}: {item['error']}\n"
        
        panel = Panel(
            summary_text.strip(),
            title="Download Results",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def show_session_summary(self):
        """Display session summary."""
        if not self.downloader:
            return
        
        summary = self.downloader.get_download_summary()
        history_stats = self.downloader.get_download_history_stats()
        
        summary_text = f"""
[bold]Session Summary[/bold]
• Session downloads: {summary['total_downloads']}
• Session size: {summary['total_size_mb']} MB
• Downloads directory: {summary['downloads_dir']}

[bold]Download History[/bold]
• Total videos in history: {history_stats['total_videos']}
• Total history size: {history_stats['total_size_mb']} MB
• Oldest download: {history_stats['oldest_download'] or 'None'}
• Newest download: {history_stats['newest_download'] or 'None'}
        """
        
        panel = Panel(
            summary_text.strip(),
            title="Session Summary",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def batch_mode(self, query: str, count: int, config_file: str = None, include_downloaded: bool = False):
        """Run in batch mode with command line arguments."""
        self.initialize_downloader(config_file)
        
        skip_downloaded = not include_downloaded
        status_msg = f"[blue]Batch mode: Searching for '{query}' (downloading {count} videos"
        if skip_downloaded:
            status_msg += ", skipping already downloaded"
        status_msg += ")[/blue]"
        rprint(status_msg)
        
        # Search for videos
        videos = self.downloader.search_videos(query, count * 2, skip_downloaded=skip_downloaded)  # Search for more options
        
        if not videos:
            rprint("[red]No videos found for your query.[/red]")
            return False
        
        # Take the top results
        selected_videos = videos[:count]
        
        rprint(f"[green]Found {len(videos)} videos, downloading top {len(selected_videos)}...[/green]")
        
        # Download videos - deduplicate URLs to ensure unique downloads
        video_urls = []
        seen_urls = set()
        for video in selected_videos:
            url = video['url']
            if url not in seen_urls:
                video_urls.append(url)
                seen_urls.add(url)
        
        if len(video_urls) < len(selected_videos):
            rprint(f"[yellow]Note: Removed {len(selected_videos) - len(video_urls)} duplicate URL(s) from download list[/yellow]")
        
        results = self.downloader.download_multiple_videos(video_urls)
        
        # Display results
        self.display_download_results(results)
        
        # Save download history
        self.downloader.save_download_history()
        
        return len(results.get('successful', [])) > 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Downloader Automation - Search and download YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s -q "funny cats" -n 5              # Download 5 funny cat videos
  %(prog)s -q "python tutorials" -n 3 -c config.yaml  # Use custom config
  %(prog)s -q "music videos" -n 10 --include-downloaded  # Include already downloaded
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Search query for YouTube videos'
    )
    
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=5,
        help='Number of videos to download (default: 5)'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode (default if no query provided)'
    )
    
    parser.add_argument(
        '--include-downloaded',
        action='store_true',
        help='Include videos that have already been downloaded (disable duplicate detection)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='YouTube Downloader Automation v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = YouTubeDownloaderCLI()
    
    # Run in appropriate mode
    if args.query and not args.interactive:
        # Batch mode
        cli.batch_mode(args.query, args.number, args.config, args.include_downloaded)
    else:
        # Interactive mode
        cli.initialize_downloader(args.config)
        cli.interactive_mode()


if __name__ == "__main__":
    main()