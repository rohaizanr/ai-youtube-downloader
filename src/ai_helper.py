"""
AI Helper Module for YouTube Downloader
Uses Gemini or ChatGPT to enhance search queries and filter results
"""

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from rich import print as rprint


class AIHelper:
    """Helper class for AI-powered search enhancement and result filtering."""
    
    def __init__(self, config: Dict):
        """
        Initialize AI Helper.
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ai_enabled = config.get('ai_enabled', False)
        self.ai_provider = config.get('ai_provider', 'gemini')
        self.search_enhancement = config.get('ai_search_enhancement', True)
        self.result_filtering = config.get('ai_result_filtering', True)
        self.max_results_to_analyze = config.get('ai_max_results_to_analyze', 30)
        
        # Setup debug logging directory
        self.debug_log_dir = Path('logs/ai_debug')
        self.debug_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI client
        self.client = None
        if self.ai_enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AI client based on provider."""
        try:
            if self.ai_provider == 'gemini':
                self._initialize_gemini()
            elif self.ai_provider == 'chatgpt':
                self._initialize_openai()
            else:
                self.logger.warning(f"Unknown AI provider: {self.ai_provider}")
                self.ai_enabled = False
        except Exception as e:
            self.logger.warning(f"Failed to initialize AI client: {e}")
            self.ai_enabled = False
    
    def _initialize_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            
            api_key = self.config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                self.logger.warning("Gemini API key not found. AI features disabled.")
                self.logger.info("Get your free API key from: https://makersuite.google.com/app/apikey")
                self.ai_enabled = False
                return
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-2.5-flash')  # Using the latest fast model
            rprint("[green]✓ Gemini AI initialized successfully[/green]")
            self.logger.info("✓ Gemini AI initialized successfully")
            
        except ImportError:
            self.logger.warning("google-generativeai not installed. Run: pip install google-generativeai")
            self.ai_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.ai_enabled = False
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            
            api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.logger.warning("OpenAI API key not found. AI features disabled.")
                self.ai_enabled = False
                return
            
            self.client = OpenAI(api_key=api_key)
            rprint("[green]✓ OpenAI initialized successfully[/green]")
            self.logger.info("✓ OpenAI initialized successfully")
            
        except ImportError:
            self.logger.warning("openai not installed. Run: pip install openai")
            self.ai_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI: {e}")
            self.ai_enabled = False
    
    def enhance_search_query(self, original_query: str) -> str:
        """
        Use AI to enhance and optimize the search query.
        
        Args:
            original_query (str): Original user search query
            
        Returns:
            str: Enhanced search query
        """
        if not self.ai_enabled or not self.search_enhancement:
            return original_query
        
        try:
            prompt = f"""You are a YouTube search expert. Convert the user's input into the BEST YouTube search keywords.

User input: "{original_query}"

INSTRUCTIONS:
1. If it's a natural language sentence/request (like "I want videos about..."), extract the CORE TOPIC
2. Remove filler words (saya, nak, yang, ada, I want, looking for, etc.)
3. Keep only the essential keywords that YouTube users actually search for
4. Use simple, popular search terms (not full sentences)
5. If in another language, keep the language but simplify to keywords
6. Focus on the MAIN subject/topic

Examples:
- "saya nak video kucing lucu" → "kucing lucu"
- "I want funny cat videos" → "funny cats"
- "saya nak semua yang ada artis malaysia takut kucing" → "artis malaysia takut kucing"
- "tutorial python for beginners please" → "python tutorial beginner"

Return ONLY the optimized search keywords (2-5 words max), nothing else.

Optimized keywords:"""

            response = self._get_ai_response(prompt, operation_type="query_enhancement")
            enhanced_query = response.strip().strip('"\'')
            
            if enhanced_query and len(enhanced_query) > 3 and enhanced_query.lower() != original_query.lower():
                rprint(f"[cyan]🤖 AI enhanced query:[/cyan] '{original_query}' → '{enhanced_query}'")
                self.logger.info(f"AI enhanced query: '{original_query}' → '{enhanced_query}'")
                return enhanced_query
            else:
                return original_query
                
        except Exception as e:
            rprint(f"[yellow]⚠ AI query enhancement failed: {e}[/yellow]")
            self.logger.warning(f"Failed to enhance search query: {e}")
            return original_query
    
    def filter_and_rank_results(self, query: str, videos: List[Dict], max_results: int, search_intent: Dict = None) -> List[Dict]:
        """
        Use AI to filter and rank search results based on relevance and user intent.
        
        Args:
            query (str): Original search query
            videos (List[Dict]): List of video information
            max_results (int): Maximum number of results to return
            search_intent (Dict): Optional search intent from get_search_intent_and_criteria
            
        Returns:
            List[Dict]: Filtered and ranked list of videos with URLs
        """
        if not self.ai_enabled or not self.result_filtering:
            return videos[:max_results]
        
        if len(videos) <= max_results:
            return videos
        
        try:
            # Analyze only a subset to avoid token limits
            videos_to_analyze = videos[:self.max_results_to_analyze]
            
            # Create a simplified list for AI analysis with URLs
            video_list = []
            for idx, video in enumerate(videos_to_analyze):
                video_list.append({
                    'index': idx,
                    'title': video.get('title', ''),
                    'channel': video.get('channel', ''),
                    'duration': video.get('duration', ''),
                    'views': video.get('views', ''),
                    'url': video.get('url', '')
                })
            
            # Build prompt based on search intent if available
            intent_context = ""
            if search_intent:
                intent_context = f"""
SEARCH INTENT ANALYSIS:
- Keywords used: {search_intent.get('keywords', query)}
- Must have: {', '.join(search_intent.get('must_have', []))}
- Priority: {', '.join(search_intent.get('priority', []))}
- Avoid: {', '.join(search_intent.get('avoid', []))}
"""
            
            prompt = f"""User's original request: "{query}"
{intent_context}
Here are YouTube video search results (in JSON format):
{json.dumps(video_list, ensure_ascii=False, indent=2)}

YOUR TASK: Select the {max_results} videos that BEST match what the user wants.

SELECTION CRITERIA:
1. **Intent Matching** (MOST IMPORTANT): Does the video actually show/contain what the user requested?
2. **Quality Indicators**: Check views, channel credibility
3. **Relevance**: Video must match the core topic, not just have similar keywords
4. **Language**: Respect the user's language (Bahasa Malaysia, English, etc.)

IMPORTANT: 
- The user wants ACTUAL videos showing their request, not just videos with similar keywords
- If user wants "celebrities afraid of cats", prioritize videos SHOWING famous people scared of cats
- Quality content that matches intent > popular videos with weak relevance

Return ONLY a JSON array of the selected video indices (just the numbers), ranked from BEST to least match.
Example format: [5, 2, 8, 1, 3]

Selected indices:"""

            response = self._get_ai_response(prompt, operation_type="result_filtering")
            
            # Parse AI response
            selected_indices = self._parse_indices(response)
            
            if selected_indices and len(selected_indices) > 0:
                rprint(f"[cyan]🤖 AI selected {len(selected_indices)} most relevant videos[/cyan]")
                self.logger.info(f"AI selected {len(selected_indices)} most relevant videos")
                
                # Return videos in the AI-recommended order
                filtered_videos = []
                for idx in selected_indices[:max_results]:
                    if 0 <= idx < len(videos_to_analyze):
                        filtered_videos.append(videos_to_analyze[idx])
                
                # Fill remaining slots if AI didn't return enough
                if len(filtered_videos) < max_results:
                    for video in videos:
                        if video not in filtered_videos and len(filtered_videos) < max_results:
                            filtered_videos.append(video)
                
                return filtered_videos
            else:
                return videos[:max_results]
                
        except Exception as e:
            self.logger.warning(f"Failed to filter results with AI: {e}")
            return videos[:max_results]
    
    def _get_ai_response(self, prompt: str, operation_type: str = "unknown") -> str:
        """
        Get response from AI provider and log the interaction.
        
        Args:
            prompt (str): Prompt to send to AI
            operation_type (str): Type of operation (e.g., "query_enhancement", "result_filtering")
            
        Returns:
            str: AI response text
        """
        # Log the prompt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_file = self.debug_log_dir / f"ai_{operation_type}_{timestamp}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "provider": self.ai_provider,
            "prompt": prompt,
            "response": None,
            "error": None
        }
        
        try:
            if self.ai_provider == 'gemini':
                response = self.client.generate_content(prompt)
                response_text = response.text
            elif self.ai_provider == 'chatgpt':
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                response_text = response.choices[0].message.content
            else:
                response_text = ""
            
            log_data["response"] = response_text
            
            # Save log to file
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"AI interaction logged to: {log_file}")
            
            return response_text
            
        except Exception as e:
            log_data["error"] = str(e)
            # Save error log
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            raise
    
    def _parse_indices(self, response: str) -> List[int]:
        """
        Parse AI response to extract video indices.
        
        Args:
            response (str): AI response text
            
        Returns:
            List[int]: List of video indices
        """
        try:
            # Try to find JSON array in response
            import re
            
            # Look for array pattern [1, 2, 3, ...]
            match = re.search(r'\[[\d,\s]+\]', response)
            if match:
                json_str = match.group(0)
                indices = json.loads(json_str)
                return [int(i) for i in indices if isinstance(i, (int, str)) and str(i).isdigit()]
            
            # Fallback: extract all numbers
            numbers = re.findall(r'\d+', response)
            return [int(n) for n in numbers]
            
        except Exception as e:
            self.logger.warning(f"Failed to parse AI response: {e}")
            return []
    
    def get_search_intent_and_criteria(self, user_query: str) -> Dict:
        """
        Use AI to understand user's search intent and generate detailed search criteria.
        
        Args:
            user_query (str): User's natural language request
            
        Returns:
            Dict: Search intent including keywords, filters, and selection criteria
        """
        if not self.ai_enabled:
            return {'keywords': user_query, 'criteria': []}
        
        try:
            prompt = f"""You are a YouTube search expert. Analyze the user's request and help find the exact videos they want.

USER REQUEST: "{user_query}"

ANALYZE THIS REQUEST AND PROVIDE:

1. **Search Keywords**: What keywords should we search on YouTube? (2-5 words, no filler words)
   - Extract the core topic
   - Remove words like "saya nak", "I want", "all videos", "yang ada", etc.
   - Keep language (Bahasa Malaysia/English) but simplify

2. **Must-Have Criteria**: What MUST the video have to match? (list specific requirements)
   Example: "must show celebrities", "must be about cats", "must show fear/phobia"

3. **Selection Priority**: What makes a video the BEST match? (rank importance)
   Example: "1. Shows famous people, 2. Features cats, 3. Shows scared reactions"

4. **Avoid**: What videos should we skip?
   Example: "skip videos about: cat care, cat food, general pet videos"

Return your analysis in this JSON format:
{{
  "keywords": "concise search terms",
  "must_have": ["requirement 1", "requirement 2"],
  "priority": ["priority 1", "priority 2", "priority 3"],
  "avoid": ["thing to avoid 1", "thing to avoid 2"]
}}

Return ONLY the JSON, nothing else:"""

            response = self._get_ai_response(prompt, operation_type="search_intent")
            
            # Parse JSON response (handle markdown code blocks)
            try:
                # Remove markdown code blocks if present
                import re
                json_text = response.strip()
                json_text = re.sub(r'```json\s*', '', json_text)
                json_text = re.sub(r'```\s*$', '', json_text)
                json_text = json_text.strip()
                
                intent = json.loads(json_text)
                rprint(f"[cyan]🤖 AI understood your intent:[/cyan]")
                rprint(f"   Keywords: [yellow]{intent.get('keywords', user_query)}[/yellow]")
                if intent.get('must_have'):
                    rprint(f"   Must have: [green]{', '.join(intent.get('must_have', [])[:2])}[/green]")
                self.logger.info(f"AI search intent: {intent}")
                return intent
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse AI JSON: {e}, response: {response[:200]}")
                # Fallback: try to extract keywords at minimum
                import re
                keywords_match = re.search(r'"keywords":\s*"([^"]+)"', response)
                if keywords_match:
                    keywords = keywords_match.group(1)
                    return {'keywords': keywords, 'must_have': [], 'priority': [], 'avoid': []}
                return {'keywords': user_query, 'must_have': [], 'priority': [], 'avoid': []}
                
        except Exception as e:
            self.logger.warning(f"Failed to get search intent: {e}")
            return {'keywords': user_query, 'must_have': [], 'priority': [], 'avoid': []}
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text."""
        # Simple language detection based on common words
        malay_words = ['saya', 'nak', 'yang', 'ada', 'dengan', 'untuk']
        english_words = ['want', 'need', 'the', 'with', 'for', 'about']
        
        text_lower = text.lower()
        malay_count = sum(1 for word in malay_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if malay_count > english_count:
            return "Bahasa Malaysia"
        elif english_count > 0:
            return "English"
        else:
            return "Unknown"
    
    def _extract_youtube_urls(self, text: str) -> List[str]:
        """Extract YouTube URLs from text."""
        import re
        
        # Pattern for YouTube URLs
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+'
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Ensure full URL format
                if not match.startswith('http'):
                    match = 'https://' + match
                if match not in urls:
                    urls.append(match)
        
        return urls
    
    def is_enabled(self) -> bool:
        """Check if AI features are enabled."""
        return self.ai_enabled
