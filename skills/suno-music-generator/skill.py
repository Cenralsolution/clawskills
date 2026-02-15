"""
Suno AI Music Generator Skill for OpenClaw
Generates music files from prompts using Suno AI API
"""

import logging
import json
import time
import requests
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import (
    ValidationError,
    SecurityError,
    get_secure_api_key,
    validate_string_input,
    safe_log_api_call,
    get_timestamp
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SunoAIMusicGenerator:
    """
    Skill to generate music files using Suno AI API.
    
    This skill takes a music prompt and uses Suno AI to generate
    a music file, then provides a download link.
    """
    
    def __init__(self):
        """Initialize the Suno AI Music Generator"""
        try:
            self.api_key = get_secure_api_key('SUNO_API_KEY')
            self.api_base_url = os.getenv('SUNO_API_BASE_URL', 'https://api.suno.ai')
            self.timeout = int(os.getenv('SUNO_TIMEOUT', '60'))
            self.max_retries = int(os.getenv('SUNO_MAX_RETRIES', '30'))
            self.retry_delay = int(os.getenv('SUNO_RETRY_DELAY', '2'))
            logger.info(f"Suno AI Music Generator initialized with base URL: {self.api_base_url}")
        except SecurityError as e:
            logger.error(f"Failed to initialize Suno AI: {e}")
            raise
    
    def generate_music(self, prompt: str, tags: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate music using Suno AI.
        
        Args:
            prompt: Music generation prompt
            tags: Optional tags for the music generation
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - file_url: Download URL for the generated music (on success)
            - song_id: ID of the generated song
            - metadata: Generation details
            - timestamp: When music was generated
            
        Raises:
            ValidationError: If prompt validation fails
        """
        try:
            # Validate input
            validated_prompt = validate_string_input(
                prompt,
                "prompt",
                min_length=10,
                max_length=2000
            )
            
            logger.info(f"Starting music generation with Suno AI")
            
            safe_log_api_call(
                "Suno AI",
                "generate_music",
                "starting",
                {"prompt_length": len(validated_prompt)}
            )
            
            # Call Suno API to initiate generation
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": validated_prompt,
                "make_instrumental": False
            }
            
            if tags:
                payload["tags"] = validate_string_input(tags, "tags", max_length=200)
            
            # Send generation request
            response = requests.post(
                f"{self.api_base_url}/v1/generate",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Suno API error: {response.status_code} - {response.text}")
                safe_log_api_call(
                    "Suno AI",
                    "generate_music",
                    "error",
                    {"status_code": response.status_code}
                )
                return {
                    "status": "error",
                    "error_type": "api_error",
                    "message": f"Suno API returned status {response.status_code}",
                    "timestamp": get_timestamp()
                }
            
            generation_data = response.json()
            song_id = generation_data.get("id")
            
            if not song_id:
                logger.error("No song ID returned from Suno API")
                return {
                    "status": "error",
                    "error_type": "invalid_response",
                    "message": "Suno API did not return a song ID",
                    "timestamp": get_timestamp()
                }
            
            logger.info(f"Music generation initiated with ID: {song_id}")
            
            # Poll for generation completion
            file_url, metadata = self._poll_for_completion(song_id, headers)
            
            if file_url:
                safe_log_api_call(
                    "Suno AI",
                    "generate_music",
                    "success",
                    {"song_id": song_id}
                )
                
                result = {
                    "status": "success",
                    "song_id": song_id,
                    "file_url": file_url,
                    "metadata": metadata,
                    "timestamp": get_timestamp()
                }
                
                logger.info(f"Music generation completed successfully: {song_id}")
                return result
            else:
                return {
                    "status": "error",
                    "error_type": "generation_timeout",
                    "message": "Music generation timed out",
                    "song_id": song_id,
                    "timestamp": get_timestamp()
                }
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except requests.exceptions.Timeout:
            logger.error("Suno API request timed out")
            safe_log_api_call("Suno AI", "generate_music", "timeout")
            return {
                "status": "error",
                "error_type": "timeout",
                "message": "Suno API request timed out",
                "timestamp": get_timestamp()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            safe_log_api_call("Suno AI", "generate_music", "error", 
                            {"error_type": "request_exception"})
            return {
                "status": "error",
                "error_type": "request_error",
                "message": f"Failed to connect to Suno API: {str(e)}",
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Unexpected error generating music: {e}")
            safe_log_api_call("Suno AI", "generate_music", "error", 
                            {"error_type": "unexpected"})
            return {
                "status": "error",
                "error_type": "unexpected",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": get_timestamp()
            }
    
    def _poll_for_completion(self, song_id: str, headers: Dict) -> tuple[Optional[str], Dict]:
        """
        Poll Suno API until music generation is complete.
        
        Args:
            song_id: ID of the generation task
            headers: HTTP headers with authorization
            
        Returns:
            Tuple of (file_url, metadata) or (None, {}) if timeout
        """
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                response = requests.get(
                    f"{self.api_base_url}/v1/songs/{song_id}",
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    song_data = response.json()
                    
                    # Check if generation is complete
                    if song_data.get("status") == "complete":
                        file_url = song_data.get("audio_url")
                        metadata = {
                            "title": song_data.get("title"),
                            "duration": song_data.get("duration"),
                            "created_at": song_data.get("created_at"),
                            "tags": song_data.get("tags")
                        }
                        logger.info(f"Music generation complete for {song_id}")
                        return file_url, metadata
                    
                    elif song_data.get("status") == "error":
                        logger.error(f"Music generation failed: {song_data.get('error_message')}")
                        return None, {"error": song_data.get("error_message")}
                    
                    # Still generating, wait and retry
                    logger.info(f"Music generation in progress ({retry_count + 1}/{self.max_retries})...")
                    time.sleep(self.retry_delay)
                    retry_count += 1
                else:
                    logger.error(f"Error fetching song status: {response.status_code}")
                    return None, {}
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling status: {e}")
                time.sleep(self.retry_delay)
                retry_count += 1
        
        logger.warning(f"Music generation polling timed out after {self.max_retries} retries")
        return None, {}


def execute_skill(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the Suno AI Music Generator skill.
    
    Args:
        parameters: OpenClaw parameters containing 'prompt'
        
    Returns:
        Result dictionary with music file URL or error
    """
    try:
        if not parameters or 'prompt' not in parameters:
            return {
                "status": "error",
                "error_type": "missing_parameter",
                "message": "Missing required parameter: 'prompt'",
                "timestamp": get_timestamp()
            }
        
        tags = parameters.get('tags', None)
        
        generator = SunoAIMusicGenerator()
        result = generator.generate_music(parameters['prompt'], tags)
        return result
        
    except SecurityError as e:
        logger.error(f"Security error in skill execution: {e}")
        return {
            "status": "error",
            "error_type": "security_error",
            "message": str(e),
            "timestamp": get_timestamp()
        }
    except Exception as e:
        logger.error(f"Unexpected error in skill execution: {e}")
        return {
            "status": "error",
            "error_type": "execution_error",
            "message": str(e),
            "timestamp": get_timestamp()
        }


if __name__ == "__main__":
    # Test execution
    test_params = {
        "prompt": "Upbeat electronic dance music with synthesizers and driving bass beat"
    }
    result = execute_skill(test_params)
    print(json.dumps(result, indent=2))
