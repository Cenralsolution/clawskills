# ChatGPT Prompt Generator Skill

## Overview

This skill generates detailed, creative music creation prompts using OpenAI's ChatGPT. It takes a user-provided theme or topic and produces a comprehensive prompt suitable for music generation AI services like Suno.

## Features

✅ **Creative Prompt Generation** - Generates music prompts with specific details about style, mood, instrumentation, and effects

✅ **Security-First Design** - API keys stored securely in environment variables, no sensitive information logged

✅ **Input Validation** - Validates theme input for length, format, and allowed characters

✅ **Error Handling** - Comprehensive error handling for rate limits, authentication, and API failures

✅ **Audit Trail** - Safe logging without exposing API keys or sensitive data

## Usage

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `theme` | string | Yes | The theme or topic for music generation (3-500 characters) |

### Output

```json
{
  "status": "success",
  "theme": "cyberpunk city at night",
  "prompt": "Create dynamic, futuristic electronic music that evokes the neon-lit streets of a cyberpunk metropolis...",
  "model": "gpt-4",
  "tokens_used": 145,
  "timestamp": "2026-02-15T10:30:45.123Z"
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4"  # Optional, defaults to gpt-4
export OPENAI_TIMEOUT="30"   # Optional, timeout in seconds
```

### 3. Configuration

Edit `config.yaml` to customize:
- OpenAI model
- API timeout
- Input validation rules

## Error Handling

The skill handles the following scenarios:

- **Validation Error**: Invalid theme (too short, too long, invalid characters)
- **Rate Limit Error**: Too many API requests to OpenAI
- **Authentication Error**: Invalid or missing API key
- **API Error**: General OpenAI API failures
- **Timeout**: Request timeout

All errors are logged safely without exposing sensitive information.

## Security Considerations

🔒 **API Key Management**
- API keys are stored only in environment variables
- API keys are never logged or exposed in responses
- Use secure environment configuration in production

🔒 **Input Validation**
- All user inputs are validated for length and format
- Special characters are sanitized

🔒 **Error Messages**
- Error messages do not reveal system internals
- API response errors are sanitized

## Testing

To test the skill locally:

```python
from skill import execute_skill

result = execute_skill({
    "theme": "tropical beach sunset"
})

print(result)
```

## Integration with OpenClaw

This skill is designed to integrate with OpenClaw's skill framework. It follows the standard skill execution interface:

- **Input**: OpenClaw parameters dictionary
- **Output**: Standard result dictionary with status, data, and timestamp
- **Error Handling**: All errors return proper error status and messages

## Next Steps

After generating a prompt, use the **Suno AI Music Generator** skill to convert the prompt into actual music, or use the **Music Generation Orchestrator** to automate the entire pipeline.

## Support

For issues or questions:
1. Check the error messages and logs
2. Verify environment variables are set correctly
3. Ensure your OpenAI API key is valid and has sufficient credits
