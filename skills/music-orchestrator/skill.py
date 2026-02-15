"""
Music Generation Orchestrator Skill for OpenClaw
Orchestrates the complete workflow: theme -> ChatGPT prompt -> Suno music generation -> download link
"""

import logging
import json
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import (
    ValidationError,
    SecurityError,
    validate_theme,
    safe_log_api_call,
    get_timestamp
)

# Import the individual skills
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from suno_music_generator.skill import SunoAIMusicGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class MusicGenerationOrchestrator:
    """
    Orchestrator skill that chains multiple AI services to generate music.
    
    Workflow:
    1. Receive theme/topic from user
    2. Generate music prompt using ChatGPT
    3. Generate music file using Suno AI
    4. Return download link
    """
    
    def __init__(self):
        """Initialize the orchestrator with required services"""
        try:
            self.chatgpt_generator = ChatGPTPromptGenerator()
            self.suno_generator = SunoAIMusicGenerator()
            logger.info("Music Generation Orchestrator initialized successfully")
        except SecurityError as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    def generate_music_from_theme(self, theme: str, tags: str = None) -> Dict[str, Any]:
        """
        Complete workflow: theme -> ChatGPT prompt -> Suno music -> download link
        
        Args:
            theme: The music theme/topic
            tags: Optional tags for Suno generation
            
        Returns:
            Dictionary containing the music file URL or error details
        """
        try:
            # Step 1: Validate theme
            validated_theme = validate_theme(theme)
            logger.info(f"Starting music generation orchestration for theme: {validated_theme}")
            
            safe_log_api_call(
                "MusicOrchestrator",
                "generate_from_theme",
                "starting",
                {"theme": validated_theme}
            )
            
            # Step 2: Generate prompt using ChatGPT
            logger.info("Step 1: Generating music prompt with ChatGPT...")
            prompt_result = self.chatgpt_generator.generate_prompt(validated_theme)
            
            if prompt_result.get("status") != "success":
                logger.error(f"Failed to generate prompt: {prompt_result.get('message')}")
                safe_log_api_call(
                    "MusicOrchestrator",
                    "generate_from_theme",
                    "error",
                    {"step": "prompt_generation", "error": prompt_result.get("message")}
                )
                return {
                    "status": "error",
                    "error_type": "prompt_generation_failed",
                    "message": f"Failed to generate prompt: {prompt_result.get('message')}",
                    "timestamp": get_timestamp()
                }
            
            generated_prompt = prompt_result.get("prompt")
            logger.info(f"Step 1 Complete: Prompt generated successfully")
            
            # Step 3: Generate music using Suno AI
            logger.info("Step 2: Generating music with Suno AI...")
            music_result = self.suno_generator.generate_music(generated_prompt, tags)
            
            if music_result.get("status") != "success":
                logger.error(f"Failed to generate music: {music_result.get('message')}")
                safe_log_api_call(
                    "MusicOrchestrator",
                    "generate_from_theme",
                    "error",
                    {"step": "music_generation", "error": music_result.get("message")}
                )
                return {
                    "status": "error",
                    "error_type": "music_generation_failed",
                    "message": f"Failed to generate music: {music_result.get('message')}",
                    "prompt": generated_prompt,
                    "timestamp": get_timestamp()
                }
            
            logger.info("Step 2 Complete: Music generated successfully")
            
            # Step 4: Return complete result
            safe_log_api_call(
                "MusicOrchestrator",
                "generate_from_theme",
                "success",
                {"theme": validated_theme, "song_id": music_result.get("song_id")}
            )
            
            result = {
                "status": "success",
                "theme": validated_theme,
                "download_url": music_result.get("file_url"),
                "song_id": music_result.get("song_id"),
                "workflow": {
                    "step1_prompt_generation": {
                        "status": "complete",
                        "generated_prompt": generated_prompt,
                        "model": prompt_result.get("model"),
                        "tokens_used": prompt_result.get("tokens_used")
                    },
                    "step2_music_generation": {
                        "status": "complete",
                        "metadata": music_result.get("metadata")
                    }
                },
                "timestamp": get_timestamp()
            }
            
            logger.info(f"Music generation orchestration completed successfully for theme: {validated_theme}")
            return result
            
        except ValidationError as e:
            logger.error(f"Validation error in orchestration: {e}")
            safe_log_api_call(
                "MusicOrchestrator",
                "generate_from_theme",
                "error",
                {"error_type": "validation"}
            )
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Unexpected error in orchestration: {e}")
            safe_log_api_call(
                "MusicOrchestrator",
                "generate_from_theme",
                "error",
                {"error_type": "unexpected"}
            )
            return {
                "status": "error",
                "error_type": "unexpected",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": get_timestamp()
            }


def execute_skill(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the Music Generation Orchestrator skill.
    
    Args:
        parameters: OpenClaw parameters containing 'theme'
        
    Returns:
        Result dictionary with download link or error
    """
    try:
        if not parameters or 'theme' not in parameters:
            return {
                "status": "error",
                "error_type": "missing_parameter",
                "message": "Missing required parameter: 'theme'",
                "timestamp": get_timestamp()
            }
        
        tags = parameters.get('tags', None)
        
        orchestrator = MusicGenerationOrchestrator()
        result = orchestrator.generate_music_from_theme(parameters['theme'], tags)
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
    test_params = {"theme": "tropical beach sunset with ocean waves"}
    result = execute_skill(test_params)
    print(json.dumps(result, indent=2))
