"""
Mubert Music Generator Skill

This skill generates music using the Mubert API.
Mubert specializes in AI-generated royalty-free music for various purposes
including background music, podcasts, streams, and content creation.

Authentication: API Key (MUBERT_API_KEY environment variable)
License: Royalty-free for personal and commercial use
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from urllib.request import urlretrieve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for shared utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils import (
    validate_string_input,
    get_secure_api_key,
    safe_log_api_call,
    validate_theme
)


class MubertMusicGenerator:
    """
    Skill for generating music using the Mubert API.
    
    Mubert provides royalty-free AI-generated music with:
    - Diverse style control
    - Duration selection
    - Commercial licenses included
    - Instant generation
    
    API Documentation: https://mubert.com/en/api
    """
    
    BASE_URL = "https://api.mubert.com/v1"
    
    # Mubert styles
    STYLES = {
        "ambient": "Ambient",
        "electronic": "Electronic",
        "lo_fi": "Lo-Fi",
        "cinematic": "Cinematic",
        "chillhop": "ChillHop",
        "synthwave": "Synthwave",
        "indie": "Indie",
        "rock": "Rock",
        "hip_hop": "Hip-Hop",
        "jazz": "Jazz",
        "classical": "Classical",
        "folk": "Folk",
        "pop": "Pop",
        "trap": "Trap",
        "tropical": "Tropical",
        "deep_house": "Deep House",
        "techno": "Techno",
        "trance": "Trance",
        "dubstep": "Dubstep",
        "metal": "Metal",
        "vocal": "Vocal",
        "soul": "Soul",
        "reggae": "Reggae"
    }
    
    # Moods/Tags
    MOODS = {
        "relaxing": "relaxing",
        "energetic": "energetic",
        "happy": "happy",
        "sad": "sad",
        "dark": "dark",
        "aggressive": "aggressive",
        "calm": "calm",
        "uplifting": "uplifting",
        "melancholic": "melancholic",
        "cute": "cute"
    }
    
    def __init__(self):
        """Initialize the Mubert Music Generator skill."""
        self.api_key = get_secure_api_key("MUBERT_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.output_dir = Path(os.getenv("MUSIC_OUTPUT_DIR", "./generated_music"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_music(
        self,
        style: str,
        duration: int = 60,
        mood: Optional[str] = None,
        text: Optional[str] = None,
        intensity: int = 5,
        polling_interval: int = 1,
        max_wait_time: int = 60
    ) -> Dict[str, Any]:
        """
        Generate music using Mubert.
        
        Args:
            style: Music style (see STYLES)
            duration: Length in seconds (10-600)
            mood: Optional mood tag (see MOODS)
            text: Optional text description for enhanced generation
            intensity: Intensity level (0-10)
            polling_interval: Seconds between status checks
            max_wait_time: Maximum seconds to wait
            
        Returns:
            Dictionary with generation results
        """
        
        validate_string_input(style, "style", min_length=3, max_length=50)
        
        if not 10 <= duration <= 600:
            raise ValueError("Duration must be between 10 and 600 seconds")
        if not 0 <= intensity <= 10:
            raise ValueError("Intensity must be between 0 and 10")
        
        # Normalize style
        style_lower = style.lower()
        if style_lower not in self.STYLES:
            available = ", ".join(self.STYLES.keys())
            raise ValueError(f"Unknown style '{style}'. Available: {available}")
        
        logger.info(f"Starting Mubert music generation with style: {style}")
        
        try:
            # Create generation request
            track_id = self._create_generation(
                style=style,
                duration=duration,
                mood=mood,
                text=text,
                intensity=intensity
            )
            
            logger.info(f"Generation created with track ID: {track_id}")
            
            # Poll for completion
            download_url = self._poll_for_completion(
                track_id=track_id,
                polling_interval=polling_interval,
                max_wait_time=max_wait_time
            )
            
            # Download audio
            file_path = self._download_audio(
                download_url=download_url,
                track_id=track_id
            )
            
            result = {
                "track_id": track_id,
                "download_url": download_url,
                "status": "completed",
                "duration": duration,
                "style": style,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "mood": mood,
                    "intensity": intensity,
                    "text_description": text,
                    "model": "Mubert",
                    "file_size": file_path.stat().st_size if file_path.exists() else 0
                }
            }
            
            safe_log_api_call("Mubert", "generate_music", "success", {
                "track_id": track_id,
                "style": style,
                "duration": duration
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Mubert music generation failed: {str(e)}", exc_info=True)
            safe_log_api_call("Mubert", "generate_music", "error", {
                "error": str(e),
                "style": style
            })
            raise
    
    def _create_generation(
        self,
        style: str,
        duration: int,
        mood: Optional[str],
        text: Optional[str],
        intensity: int
    ) -> str:
        """Create a generation request on Mubert."""
        
        payload = {
            "style": style,
            "duration": duration,
            "intensity": intensity
        }
        
        if mood and mood.lower() in self.MOODS:
            payload["tags"] = [mood.lower()]
        
        if text:
            payload["text"] = text[:100]  # Limit text length
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/generate",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                raise RuntimeError(data.get("error", "Generation creation failed"))
            
            track_id = data.get("track_id") or data.get("id")
            return track_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create generation: {str(e)}")
            raise
    
    def _poll_for_completion(
        self,
        track_id: str,
        polling_interval: int = 1,
        max_wait_time: int = 60
    ) -> str:
        """Poll Mubert API until generation is complete."""
        
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/status/{track_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") == "ready":
                    download_url = data.get("download_url")
                    logger.info(f"Generation completed after {poll_count} polls")
                    return download_url
                
                elif data.get("status") == "failed":
                    raise RuntimeError(f"Generation failed: {data.get('error', 'Unknown error')}")
                
                logger.info(f"Poll #{poll_count}: Status = {data.get('status')}")
                time.sleep(polling_interval)
                
            except requests.RequestException as e:
                logger.warning(f"Error polling status: {str(e)}")
                time.sleep(polling_interval)
        
        raise TimeoutError(f"Generation did not complete within {max_wait_time} seconds")
    
    def _download_audio(self, download_url: str, track_id: str) -> Path:
        """Download generated audio file."""
        
        try:
            file_path = self.output_dir / f"mubert_{track_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            urlretrieve(download_url, file_path)
            
            logger.info(f"Audio saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download audio: {str(e)}")
            raise
    
    def execute_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Mubert Music Generator skill.
        
        Input format:
        {
            "style": "ambient",
            "duration": 120,
            "mood": "relaxing",
            "intensity": 3
        }
        """
        
        try:
            result = self.generate_music(
                style=input_data.get("style", "ambient"),
                duration=input_data.get("duration", 60),
                mood=input_data.get("mood"),
                text=input_data.get("text"),
                intensity=input_data.get("intensity", 5),
                polling_interval=input_data.get("polling_interval", 1),
                max_wait_time=input_data.get("max_wait_time", 60)
            )
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Skill execution failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    @staticmethod
    def list_styles() -> Dict[str, str]:
        """List all available styles."""
        return MubertMusicGenerator.STYLES
    
    @staticmethod
    def list_moods() -> Dict[str, str]:
        """List all available moods."""
        return MubertMusicGenerator.MOODS


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill."""
    return {
        "name": "Mubert Music Generator",
        "version": "1.0.0",
        "description": "Generate royalty-free music using Mubert API",
        "provider": "Mubert",
        "licenses": ["Royalty-free", "Commercial-allowed"],
        "capabilities": [
            "text-to-audio",
            "style-control",
            "mood-control",
            "intensity-control",
            "various-durations"
        ],
        "input_schema": {
            "style": "string (required, see STYLES)",
            "duration": "integer (10-600 seconds)",
            "mood": "string (optional, see MOODS)",
            "text": "string (optional, additional description)",
            "intensity": "integer (0-10)"
        }
    }
