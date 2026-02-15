"""
AIVA Music Generator Skill

This skill generates music from text prompts using the AIVA API.
AIVA (Artificial Intelligence Virtual Artist) provides state-of-the-art
music generation with high-quality audio output.

Authentication: API Key (AIVA_API_KEY environment variable)
Rate Limits: Check AIVA documentation for current limits
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

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


class AIVAMusicGenerator:
    """
    Skill for generating music using the AIVA API.
    
    AIVA provides professional-grade music generation with support for
    various genres, moods, and orchestration styles.
    
    API Documentation: https://www.aiva.ai/api
    """
    
    BASE_URL = "https://api.aiva.ai/v1"
    
    def __init__(self):
        """Initialize the AIVA Music Generator skill."""
        self.api_key = get_secure_api_key("AIVA_API_KEY")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        self.output_dir = Path(os.getenv("MUSIC_OUTPUT_DIR", "./generated_music"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        genre: str = "ambient",
        mood: str = "calm",
        tempo: int = 90,
        key: str = "C major",
        polling_interval: int = 2,
        max_wait_time: int = 300
    ) -> Dict[str, Any]:
        """
        Generate music from a text prompt using AIVA.
        
        Args:
            prompt: Text description of desired music
            duration: Length of generated music in seconds (15-120)
            genre: Musical genre (e.g., "ambient", "orchestral", "electronic")
            mood: Emotional tone (e.g., "calm", "energetic", "dark")
            tempo: BPM (beats per minute)
            key: Musical key (e.g., "C major", "A minor")
            polling_interval: Seconds between status checks
            max_wait_time: Maximum seconds to wait for completion
            
        Returns:
            Dictionary with music generation results including:
            - composition_id: Unique identifier for the composition
            - audio_url: URL to download the generated audio
            - status: Generation status ("completed", "processing", "failed")
            - duration: Length of generated music
            - file_path: Local path where audio was saved
            - metadata: Additional information about the composition
        """
        
        # Validate inputs
        validate_string_input(prompt, "prompt", min_length=10, max_length=500)
        validate_theme(genre, "genre")
        validate_theme(mood, "mood")
        
        if not 15 <= duration <= 120:
            raise ValueError("Duration must be between 15 and 120 seconds")
        if not 40 <= tempo <= 240:
            raise ValueError("Tempo must be between 40 and 240 BPM")
            
        logger.info(f"Starting AIVA music generation with prompt: {prompt[:100]}...")
        
        try:
            # Step 1: Create composition
            composition_id = self._create_composition(
                prompt=prompt,
                duration=duration,
                genre=genre,
                mood=mood,
                tempo=tempo,
                key=key
            )
            
            logger.info(f"Composition created with ID: {composition_id}")
            
            # Step 2: Generate the music
            generation_id = self._trigger_generation(composition_id)
            logger.info(f"Generation triggered with ID: {generation_id}")
            
            # Step 3: Poll for completion
            audio_url = self._poll_for_completion(
                generation_id=generation_id,
                composition_id=composition_id,
                polling_interval=polling_interval,
                max_wait_time=max_wait_time
            )
            
            # Step 4: Download and save audio
            file_path = self._download_audio(
                audio_url=audio_url,
                composition_id=composition_id
            )
            
            result = {
                "composition_id": composition_id,
                "generation_id": generation_id,
                "audio_url": audio_url,
                "status": "completed",
                "duration": duration,
                "genre": genre,
                "mood": mood,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "prompt": prompt,
                    "tempo": tempo,
                    "key": key,
                    "model": "AIVA",
                    "file_size": file_path.stat().st_size if file_path.exists() else 0
                }
            }
            
            safe_log_api_call("AIVA", "generate_music", "success", {
                "composition_id": composition_id,
                "duration": duration,
                "genre": genre
            })
            
            return result
            
        except Exception as e:
            logger.error(f"AIVA music generation failed: {str(e)}", exc_info=True)
            safe_log_api_call("AIVA", "generate_music", "error", {
                "error": str(e),
                "prompt": prompt[:50]
            })
            raise
    
    def _create_composition(
        self,
        prompt: str,
        duration: int,
        genre: str,
        mood: str,
        tempo: int,
        key: str
    ) -> str:
        """Create a composition with AIVA."""
        
        payload = {
            "title": f"Generated {genre} composition",
            "description": prompt,
            "duration": duration,
            "genre": genre,
            "mood": mood,
            "tempo": tempo,
            "musicKey": key
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/compositions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("id") or data.get("composition_id")
            
        except requests.RequestException as e:
            logger.error(f"Failed to create composition: {str(e)}")
            raise
    
    def _trigger_generation(self, composition_id: str) -> str:
        """Trigger generation for a composition."""
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/compositions/{composition_id}/generate",
                json={"quality": "high"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("id") or data.get("generation_id")
            
        except requests.RequestException as e:
            logger.error(f"Failed to trigger generation: {str(e)}")
            raise
    
    def _poll_for_completion(
        self,
        generation_id: str,
        composition_id: str,
        polling_interval: int = 2,
        max_wait_time: int = 300
    ) -> str:
        """Poll AIVA API until generation is complete."""
        
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/generations/{generation_id}/status",
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                status = data.get("status", "processing").lower()
                
                if status == "completed" or status == "done":
                    logger.info(f"Generation completed after {poll_count} polls")
                    return data.get("audio_url") or data.get("downloadURL")
                    
                elif status == "failed" or status == "error":
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Generation failed: {error_msg}")
                    raise RuntimeError(f"AIVA generation failed: {error_msg}")
                    
                logger.info(f"Poll #{poll_count}: Status = {status}")
                time.sleep(polling_interval)
                
            except requests.RequestException as e:
                logger.warning(f"Error polling generation status: {str(e)}")
                time.sleep(polling_interval)
        
        raise TimeoutError(f"Generation did not complete within {max_wait_time} seconds")
    
    def _download_audio(self, audio_url: str, composition_id: str) -> Path:
        """Download generated audio file."""
        
        try:
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', 'audio/wav')
            extension = 'wav' if 'wav' in content_type else 'mp3'
            
            file_path = self.output_dir / f"aiva_{composition_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Audio saved to {file_path}")
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download audio: {str(e)}")
            raise
    
    def execute_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the AIVA Music Generator skill.
        
        Input format:
        {
            "prompt": "orchestral theme with strings and brass",
            "duration": 60,
            "genre": "orchestral",
            "mood": "epic",
            "tempo": 120,
            "key": "D major"
        }
        """
        
        try:
            result = self.generate_music(
                prompt=input_data.get("prompt", ""),
                duration=input_data.get("duration", 30),
                genre=input_data.get("genre", "ambient"),
                mood=input_data.get("mood", "calm"),
                tempo=input_data.get("tempo", 90),
                key=input_data.get("key", "C major"),
                polling_interval=input_data.get("polling_interval", 2),
                max_wait_time=input_data.get("max_wait_time", 300)
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


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill."""
    return {
        "name": "AIVA Music Generator",
        "version": "1.0.0",
        "description": "Generate professional music using AIVA AI",
        "provider": "AIVA",
        "capabilities": [
            "text-to-music",
            "genre-control",
            "mood-control",
            "tempo-control",
            "key-control"
        ],
        "input_schema": {
            "prompt": "string (required, 10-500 chars)",
            "duration": "integer (15-120 seconds)",
            "genre": "string (ambient, orchestral, electronic, etc.)",
            "mood": "string (calm, energetic, dark, happy, etc.)",
            "tempo": "integer (40-240 BPM)",
            "key": "string (e.g., C major, A minor)",
            "polling_interval": "integer (seconds between status checks)",
            "max_wait_time": "integer (max seconds to wait)"
        },
        "output_schema": {
            "composition_id": "string",
            "generation_id": "string",
            "audio_url": "string",
            "file_path": "string",
            "status": "string (completed/processing/failed)",
            "metadata": "object"
        }
    }
