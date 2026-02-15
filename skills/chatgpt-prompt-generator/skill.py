"""
ChatGPT Prompt Generator Skill for OpenClaw
Generates music creation prompts based on themes provided by the user
"""

import logging
import json
from typing import Dict, Any, Optional
import openai
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import (
    ValidationError, 
    SecurityError,
    get_secure_api_key,
    validate_theme,
    safe_log_api_call,
    get_timestamp
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ChatGPTPromptGenerator:
    """
    Skill to generate music creation prompts using ChatGPT.
    
    This skill takes a theme/topic and uses ChatGPT to create a detailed
    music generation prompt that can be used by music AI services like Suno.
    """
    
    SYSTEM_PROMPT = """You are a creative music prompt expert. Your task is to generate 
detailed, inspiring prompts for music generation AI. When given a theme or topic, create 
a comprehensive prompt that includes:
- Musical style/genre
- Mood and atmosphere
- Instrumentation suggestions
- Tempo and rhythm suggestions
- Any special effects or techniques
- Duration suggestion

Keep prompts focused and between 100-300 words. Be creative but practical."""

    def __init__(self):
        """Initialize the ChatGPT Prompt Generator"""
        try:
            self.api_key = get_secure_api_key('OPENAI_API_KEY')
            openai.api_key = self.api_key
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
            self.timeout = int(os.getenv('OPENAI_TIMEOUT', '30'))
            logger.info(f"ChatGPT Prompt Generator initialized with model: {self.model}")
        except SecurityError as e:
            logger.error(f"Failed to initialize ChatGPT: {e}")
            raise
    
    def generate_prompt(self, theme: str) -> Dict[str, Any]:
        """
        Generate a music creation prompt for the given theme.
        
        Args:
            theme: The theme or topic for music generation (e.g., "rainy evening", "space exploration")
            
        Returns:
            Dictionary containing:
            - prompt: Generated music prompt
            - theme: Original theme
            - model: Model used
            - timestamp: When the prompt was generated
            - status: 'success' or 'error'
            
        Raises:
            ValidationError: If theme validation fails
            Exception: If ChatGPT API call fails
        """
        try:
            # Validate input
            validated_theme = validate_theme(theme)
            logger.info(f"Generating prompt for theme: {validated_theme}")
            
            # Prepare the user message
            user_message = f"Create a detailed music generation prompt for the theme: '{validated_theme}'"
            
            # Call ChatGPT API
            safe_log_api_call(
                "OpenAI/ChatGPT",
                "generate_Music_prompt",
                "starting",
                {"theme": validated_theme, "model": self.model}
            )
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=self.timeout
            )
            
            generated_prompt = response.choices[0].message.content.strip()
            
            safe_log_api_call(
                "OpenAI/ChatGPT",
                "generate_music_prompt",
                "success",
                {"theme": validated_theme, "prompt_length": len(generated_prompt)}
            )
            
            result = {
                "status": "success",
                "theme": validated_theme,
                "prompt": generated_prompt,
                "model": self.model,
                "timestamp": get_timestamp(),
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
            logger.info(f"Successfully generated prompt for theme: {validated_theme}")
            return result
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except openai.error.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            safe_log_api_call("OpenAI/ChatGPT", "generate_music_prompt", "error", 
                            {"error_type": "rate_limit"})
            return {
                "status": "error",
                "error_type": "rate_limit",
                "message": "OpenAI API rate limit exceeded. Please try again later.",
                "timestamp": get_timestamp()
            }
        except openai.error.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            safe_log_api_call("OpenAI/ChatGPT", "generate_music_prompt", "error", 
                            {"error_type": "authentication"})
            return {
                "status": "error",
                "error_type": "authentication",
                "message": "Failed to authenticate with OpenAI API.",
                "timestamp": get_timestamp()
            }
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            safe_log_api_call("OpenAI/ChatGPT", "generate_music_prompt", "error", 
                            {"error_type": "openai_api"})
            return {
                "status": "error",
                "error_type": "openai_api",
                "message": f"OpenAI API error: {str(e)}",
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Unexpected error generating prompt: {e}")
            safe_log_api_call("OpenAI/ChatGPT", "generate_music_prompt", "error", 
                            {"error_type": "unexpected"})
            return {
                "status": "error",
                "error_type": "unexpected",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": get_timestamp()
            }


def execute_skill(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the ChatGPT Prompt Generator skill.
    
    Args:
        parameters: OpenClaw parameters containing 'theme'
        
    Returns:
        Result dictionary with generated prompt or error
    """
    try:
        if not parameters or 'theme' not in parameters:
            return {
                "status": "error",
                "error_type": "missing_parameter",
                "message": "Missing required parameter: 'theme'",
                "timestamp": get_timestamp()
            }
        
        generator = ChatGPTPromptGenerator()
        result = generator.generate_prompt(parameters['theme'])
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
    test_params = {"theme": "cyberpunk city at night"}
    result = execute_skill(test_params)
    print(json.dumps(result, indent=2))
