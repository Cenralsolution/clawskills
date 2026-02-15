"""
Soundraw Music Generator Skill

This skill generates unique, customizable music using the Soundraw API.
Soundraw provides AI-generated royalty-free music with extensive customization
options for genre, mood, and instrumentation.

Authentication: API Key (SOUNDRAW_API_KEY environment variable)
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


class SoundrawMusicGenerator:
    """
    Skill for generating music using the Soundraw API.
    
    Soundraw offers:
    - AI-generated original music
    - Extensive customization options
    - Royalty-free commercial licenses
    - Multiple audio format options
    - Real-time music variation
    
    API Documentation: https://www.soundraw.io/api
    """
    
    BASE_URL = "https://api.soundraw.io"
    
    # Soundraw genres
    GENRES = [
        "ambient", "acoustic", "blues", "classical", "country", "dance", "electronic",
        "funk", "hip_hop", "jazz", "latin", "metal", "pop", "punk", "reggae", "rnb",
        "rock", "soul", "world", "cinematic", "experimental", "indie"
    ]
    
    # Soundraw moods
    MOODS = [
        "aggressive", "angry", "bright", "calm", "cheerful", "cinematic", "dark",
        "delicate", "dramatic", "dreamy", "driven", "emotional", "energetic",
        "epic", "ethereal", "exploratory", "gloomy", "happy", "hopeful", "hypnotic",
        "intense", "introspective", "joyful", "light", "lonely", "meditative",
        "melancholic", "mellow", "menacing", "moody", "mysterious", "nostalgic",
        "peaceful", "playful", "proud", "relaxed", "romantic", "sad", "serene",
        "sophisticated", "tense", "uplifting", "urgent", "victorious", "vintage"
    ]
    
    def __init__(self):
        """Initialize the Soundraw Music Generator skill."""
        self.api_key = get_secure_api_key("SOUNDRAW_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.output_dir = Path(os.getenv("MUSIC_OUTPUT_DIR", "./generated_music"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_music(
        self,
        genre: str,
        mood: str,
        duration: int = 60,
        instrumentation: Optional[str] = None,
        tempo: Optional[int] = None,
        energy: int = 5,
        polling_interval: int = 2,
        max_wait_time: int = 180
    ) -> Dict[str, Any]:
        """
        Generate music using Soundraw.
        
        Args:
            genre: Music genre (see GENRES)
            mood: Emotional tone (see MOODS)
            duration: Length in seconds (10-600)
            instrumentation: Optional string describing instruments
            tempo: Optional tempo in BPM
            energy: Energy level (1-10)
            polling_interval: Seconds between status checks
            max_wait_time: Maximum seconds to wait
            
        Returns:
            Dictionary with generation results
        """
        
        validate_string_input(genre, "genre", min_length=3, max_length=50)
        validate_string_input(mood, "mood", min_length=3, max_length=50)
        
        if not 10 <= duration <= 600:
            raise ValueError("Duration must be between 10 and 600 seconds")
        if not 1 <= energy <= 10:
            raise ValueError("Energy must be between 1 and 10")
        
        # Validate genre and mood
        genre_lower = genre.lower()
        mood_lower = mood.lower()
        
        if genre_lower not in self.GENRES:
            raise ValueError(f"Unknown genre '{genre}'. Available: {', '.join(self.GENRES)}")
        if mood_lower not in self.MOODS:
            raise ValueError(f"Unknown mood '{mood}'. Available: {', '.join(self.MOODS[:10])}... (and more)")
        
        logger.info(f"Starting Soundraw music generation: {genre} - {mood}")
        
        try:
            # Create generation request
            track_id = self._create_generation(
                genre=genre,
                mood=mood,
                duration=duration,
                instrumentation=instrumentation,
                tempo=tempo,
                energy=energy
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
                "genre": genre,
                "mood": mood,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "instrumentation": instrumentation,
                    "tempo": tempo,
                    "energy": energy,
                    "model": "Soundraw",
                    "file_size": file_path.stat().st_size if file_path.exists() else 0
                }
            }
            
            safe_log_api_call("Soundraw", "generate_music", "success", {
                "track_id": track_id,
                "genre": genre,
                "mood": mood
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Soundraw music generation failed: {str(e)}", exc_info=True)
            safe_log_api_call("Soundraw", "generate_music", "error", {
                "error": str(e),
                "genre": genre,
                "mood": mood
            })
            raise
    
    def _create_generation(
        self,
        genre: str,
        mood: str,
        duration: int,
        instrumentation: Optional[str],
        tempo: Optional[int],
        energy: int
    ) -> str:
        """Create a generation request on Soundraw."""
        
        payload = {
            "genre": genre.lower(),
            "mood": mood.lower(),
            "duration": duration,
            "energy": energy
        }
        
        if instrumentation:
            payload["instrumentation"] = instrumentation
        
        if tempo:
            payload["tempo"] = tempo
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/v1/songs",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success") and "error" in data:
                raise RuntimeError(data.get("error", "Generation creation failed"))
            
            track_id = data.get("track_id") or data.get("id") or data.get("song_id")
            
            if not track_id:
                raise RuntimeError("No track ID in response")
            
            return track_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create generation: {str(e)}")
            raise
    
    def _poll_for_completion(
        self,
        track_id: str,
        polling_interval: int = 2,
        max_wait_time: int = 180
    ) -> str:
        """Poll Soundraw API until generation is complete."""
        
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/api/v1/songs/{track_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                status = data.get("status", "generating").lower()
                
                if status == "completed" or status == "ready":
                    download_url = data.get("download_url") or data.get("audio_url")
                    logger.info(f"Generation completed after {poll_count} polls")
                    return download_url
                
                elif status == "failed":
                    error_msg = data.get("error", "Unknown error")
                    raise RuntimeError(f"Generation failed: {error_msg}")
                
                logger.info(f"Poll #{poll_count}: Status = {status}")
                time.sleep(polling_interval)
                
            except requests.RequestException as e:
                logger.warning(f"Error polling status: {str(e)}")
                time.sleep(polling_interval)
        
        raise TimeoutError(f"Generation did not complete within {max_wait_time} seconds")
    
    def _download_audio(self, download_url: str, track_id: str) -> Path:
        """Download generated audio file."""
        
        try:
            file_path = self.output_dir / f"soundraw_{track_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            urlretrieve(download_url, file_path)
            
            logger.info(f"Audio saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download audio: {str(e)}")
            raise
    
    def execute_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Soundraw Music Generator skill.
        
        Input format:
        {
            "genre": "orchestral",
            "mood": "epic",
            "duration": 90,
            "instrumentation": "full orchestra with strings and brass",
            "tempo": 120,
            "energy": 8
        }
        """
        
        try:
            result = self.generate_music(
                genre=input_data.get("genre", "ambient"),
                mood=input_data.get("mood", "calm"),
                duration=input_data.get("duration", 60),
                instrumentation=input_data.get("instrumentation"),
                tempo=input_data.get("tempo"),
                energy=input_data.get("energy", 5),
                polling_interval=input_data.get("polling_interval", 2),
                max_wait_time=input_data.get("max_wait_time", 180)
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
    def list_genres() -> list:
        """List all available genres."""
        return SoundrawMusicGenerator.GENRES
    
    @staticmethod
    def list_moods() -> list:
        """List all available moods."""
        return SoundrawMusicGenerator.MOODS


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill."""
    return {
        "name": "Soundraw Music Generator",
        "version": "1.0.0",
        "description": "Generate original AI music using Soundraw API",
        "provider": "Soundraw",
        "licenses": ["Royalty-free", "Commercial-allowed"],
        "capabilities": [
            "text-to-audio",
            "genre-control",
            "mood-control",
            "instrumentation-specification",
            "tempo-control",
            "energy-control"
        ],
        "input_schema": {
            "genre": "string (required, see GENRES)",
            "mood": "string (required, see MOODS)",
            "duration": "integer (10-600 seconds)",
            "instrumentation": "string (optional)",
            "tempo": "integer (optional, in BPM)",
            "energy": "integer (1-10)"
        }
    }
