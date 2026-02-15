"""
Replicate Music Generator Skill

This skill generates music using Replicate API, which hosts various
music generation models including Meta's MusicGen, Stable Audio, and others.

Authentication: API Token (REPLICATE_API_TOKEN environment variable)
Available Models: MusicGen, Jukebox, Riffusion, and more
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
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


class ReplicateMusicGenerator:
    """
    Skill for generating music using Replicate API.
    
    Replicate hosts multiple music generation models:
    - musicgen: Meta's MusicGen model (text-to-audio)
    - stable-audio: Stability AI's Stable Audio (text-to-audio)
    - jukebox: OpenAI's Jukebox (music generation)
    - riffusion: Riffusion model (spectrogram-based generation)
    
    API Documentation: https://replicate.com/docs
    Model Documentation: https://replicate.com/explore
    """
    
    BASE_URL = "https://api.replicate.com/v1"
    
    # Available models on Replicate
    MODELS = {
        "musicgen": {
            "id": "facebook/musicgen",
            "full_id": "facebook/musicgen:7a76a47476de1ea6299c4d6fe53dd8c33ef1ae38490def302445efc6037f7b50",
            "description": "Meta's MusicGen - highest quality text-to-audio",
            "best_for": "professional compositions, diverse genres"
        },
        "musicgen-large": {
            "id": "facebook/musicgen",
            "full_id": "facebook/musicgen:1c39d20554b8435f94e85304fde3a19186530fde3c6c91729271d8a8ca2cdc66",
            "description": "MusicGen Large model - improved quality and duration",
            "best_for": "longer compositions, complex arrangements"
        },
        "stable-audio": {
            "id": "stability-ai/stable-audio",
            "full_id": "stability-ai/stable-audio:cae302ffa8b4a7b8b3c1e3e6c1e3e6c1e3e6c1e3e6c1e3e6c1e3e6c1e3e6",
            "description": "Stability AI's audio generation model",
            "best_for": "various audio effects and minimal music"
        }
    }
    
    def __init__(self, model: str = "musicgen"):
        """
        Initialize the Replicate Music Generator skill.
        
        Args:
            model: Model to use ("musicgen", "musicgen-large", "stable-audio")
        """
        self.api_token = get_secure_api_key("REPLICATE_API_TOKEN")
        self.model = model.lower()
        
        if self.model not in self.MODELS:
            available = ", ".join(self.MODELS.keys())
            raise ValueError(f"Unknown model '{model}'. Available: {available}")
        
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        
        self.output_dir = Path(os.getenv("MUSIC_OUTPUT_DIR", "./generated_music"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        temperature: float = 1.0,
        top_k: int = 250,
        top_p: float = 0.0,
        polling_interval: int = 2,
        max_wait_time: int = 600
    ) -> Dict[str, Any]:
        """
        Generate music from a text prompt using Replicate.
        
        Args:
            prompt: Text description of desired music
            duration: Length of generated music in seconds (5-30)
            temperature: Randomness of generation (0.0-1.0), higher = more creative
            top_k: Diversity parameter for sampling
            top_p: Nucleus sampling parameter (0.0-1.0)
            polling_interval: Seconds between status checks
            max_wait_time: Maximum seconds to wait for completion
            
        Returns:
            Dictionary with music generation results including:
            - prediction_id: Unique identifier for the generation
            - output_url: URL to the generated audio file
            - status: Generation status
            - duration: Length of generated music
            - file_path: Local path where audio was saved
            - metadata: Additional information
        """
        
        # Validate inputs
        validate_string_input(prompt, "prompt", min_length=5, max_length=500)
        
        if not 5 <= duration <= 30:
            raise ValueError("Duration must be between 5 and 30 seconds for Replicate")
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
        logger.info(f"Starting Replicate music generation with model {self.model}")
        logger.info(f"Prompt: {prompt[:100]}...")
        
        try:
            # Get model information
            model_info = self.MODELS[self.model]
            model_full_id = model_info["full_id"]
            
            # Create prediction (async job)
            prediction_id = self._create_prediction(
                model_id=model_full_id,
                prompt=prompt,
                duration=duration,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p
            )
            
            logger.info(f"Prediction created with ID: {prediction_id}")
            
            # Poll for completion
            output_url = self._poll_for_completion(
                prediction_id=prediction_id,
                polling_interval=polling_interval,
                max_wait_time=max_wait_time
            )
            
            # Download and save audio
            file_path = self._download_audio(
                audio_url=output_url,
                prediction_id=prediction_id
            )
            
            result = {
                "prediction_id": prediction_id,
                "output_url": output_url,
                "status": "completed",
                "duration": duration,
                "model": self.model,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "prompt": prompt,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "model_provider": "Replicate",
                    "file_size": file_path.stat().st_size if file_path.exists() else 0
                }
            }
            
            safe_log_api_call("Replicate", "generate_music", "success", {
                "prediction_id": prediction_id,
                "model": self.model,
                "duration": duration
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Replicate music generation failed: {str(e)}", exc_info=True)
            safe_log_api_call("Replicate", "generate_music", "error", {
                "error": str(e),
                "prompt": prompt[:50]
            })
            raise
    
    def _create_prediction(
        self,
        model_id: str,
        prompt: str,
        duration: int,
        temperature: float,
        top_k: int,
        top_p: float
    ) -> str:
        """Create a prediction (async job) on Replicate."""
        
        payload = {
            "version": model_id,
            "input": {
                "prompt": prompt,
                "duration": duration,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/predictions",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            prediction_id = data.get("id")
            
            if not prediction_id:
                raise RuntimeError("No prediction ID in response")
            
            return prediction_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create prediction: {str(e)}")
            raise
    
    def _poll_for_completion(
        self,
        prediction_id: str,
        polling_interval: int = 2,
        max_wait_time: int = 600
    ) -> str:
        """Poll Replicate API until prediction is complete."""
        
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/predictions/{prediction_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                status = data.get("status", "processing").lower()
                
                if status == "succeeded":
                    output = data.get("output")
                    
                    if isinstance(output, list) and len(output) > 0:
                        output_url = output[0]
                    else:
                        output_url = output
                    
                    logger.info(f"Prediction completed after {poll_count} polls")
                    return output_url
                    
                elif status == "failed":
                    error = data.get("error", "Unknown error")
                    logger.error(f"Prediction failed: {error}")
                    raise RuntimeError(f"Replicate prediction failed: {error}")
                    
                logger.info(f"Poll #{poll_count}: Status = {status}")
                time.sleep(polling_interval)
                
            except requests.RequestException as e:
                logger.warning(f"Error polling prediction status: {str(e)}")
                time.sleep(polling_interval)
        
        raise TimeoutError(f"Prediction did not complete within {max_wait_time} seconds")
    
    def _download_audio(self, audio_url: str, prediction_id: str) -> Path:
        """Download generated audio file."""
        
        try:
            file_path = self.output_dir / f"replicate_{prediction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            urlretrieve(audio_url, file_path)
            
            logger.info(f"Audio saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download audio: {str(e)}")
            raise
    
    def execute_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Replicate Music Generator skill.
        
        Input format:
        {
            "prompt": "upbeat electronic dance music with deep bass",
            "duration": 20,
            "temperature": 0.8,
            "top_k": 250,
            "top_p": 0.0
        }
        """
        
        try:
            result = self.generate_music(
                prompt=input_data.get("prompt", ""),
                duration=input_data.get("duration", 30),
                temperature=input_data.get("temperature", 1.0),
                top_k=input_data.get("top_k", 250),
                top_p=input_data.get("top_p", 0.0),
                polling_interval=input_data.get("polling_interval", 2),
                max_wait_time=input_data.get("max_wait_time", 600)
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
    def list_available_models() -> Dict[str, Dict[str, str]]:
        """Return information about available models."""
        return ReplicateMusicGenerator.MODELS


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill."""
    return {
        "name": "Replicate Music Generator",
        "version": "1.0.0",
        "description": "Generate music using Replicate API and various AI models",
        "provider": "Replicate",
        "available_models": list(ReplicateMusicGenerator.MODELS.keys()),
        "capabilities": [
            "text-to-audio",
            "multiple-models",
            "temperature-control",
            "configurable-parameters"
        ],
        "input_schema": {
            "prompt": "string (required, 5-500 chars)",
            "duration": "integer (5-30 seconds)",
            "temperature": "float (0.0-1.0, higher = more random)",
            "top_k": "integer (diversity parameter)",
            "top_p": "float (0.0-1.0, nucleus sampling)"
        }
    }
