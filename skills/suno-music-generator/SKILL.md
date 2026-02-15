# Suno AI Music Generator Skill

## Overview

This skill generates music files using Suno AI's API. It takes a music generation prompt (typically created by the ChatGPT Prompt Generator) and produces an audio file that can be downloaded.

## Features

✅ **Music File Generation** - Generates high-quality music files from detailed prompts

✅ **Asynchronous Polling** - Handles long-running generation tasks with intelligent polling and retry mechanisms

✅ **Timeout Protection** - Prevents hanging requests with configurable timeouts

✅ **Security-First Design** - API keys stored securely, sensitive data never logged

✅ **Comprehensive Error Handling** - Handles API errors, timeouts, and network issues gracefully

✅ **Metadata Extraction** - Returns song metadata including title, duration, and creation timestamp

## Usage

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Music generation prompt (10-2000 characters) |
| `tags` | string | No | Optional tags for the generation (max 200 characters) |

### Output

```json
{
  "status": "success",
  "song_id": "song_abc123def456",
  "file_url": "https://cdn.suno.ai/music/song_abc123def456.mp3",
  "metadata": {
    "title": "Cyberpunk Nights",
    "duration": 180,
    "created_at": "2026-02-15T10:35:20Z",
    "tags": "electronic,cyberpunk,atmospheric"
  },
  "timestamp": "2026-02-15T10:35:45.123Z"
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export SUNO_API_KEY="your-suno-api-key"
export SUNO_API_BASE_URL="https://api.suno.ai"  # Optional
export SUNO_TIMEOUT="60"         # Optional, timeout in seconds
export SUNO_MAX_RETRIES="30"     # Optional, max polling retries
export SUNO_RETRY_DELAY="2"      # Optional, delay between retries
```

### 3. Configuration

Edit `config.yaml` to customize:
- API timeout duration
- Maximum polling retries
- Retry delay between polls
- Base API URL

## How It Works

### Generation Flow

1. **Send Request**: Sends the prompt to Suno AI API to initiate music generation
2. **Get Song ID**: Receives a unique song ID for tracking
3. **Poll for Completion**: Repeatedly checks the API until generation completes (max 30 retries)
4. **Return Result**: Returns the download URL and metadata

### Polling Strategy

- **Initial Delay**: 2 seconds between polls (configurable)
- **Max Retries**: 30 attempts (configurable)
- **Total Wait Time**: Up to ~60 seconds with default settings
- **Timeout Protection**: Any single API call times out after 60 seconds

## Error Handling

The skill handles the following scenarios:

- **Validation Error**: Invalid prompt (too short, too long)
- **API Error**: Suno API returns error status code
- **Generation Failure**: Music generation fails on Suno's side
- **Timeout**: Generation takes too long
- **Network Error**: Connection issues with Suno API
- **Invalid Response**: API returns unexpected data format

All errors are logged safely without exposing API keys.

## Security Considerations

🔒 **API Key Management**
- API keys stored only in environment variables
- Never logged or exposed in responses
- Use secure environment configuration in production

🔒 **Data Privacy**
- Generated files are hosted by Suno
- URLs expire according to Suno's retention policy
- Download links should be passed to users immediately

🔒 **Input Validation**
- Prompts are validated for length and format
- Prevents injection attacks

## Testing

To test the skill locally:

```python
from skill import execute_skill

result = execute_skill({
    "prompt": "Upbeat electronic dance music with driving bass beat",
    "tags": "electronic,dance,upbeat"
})

print(result)
```

## Performance Considerations

⏱️ **Expected Generation Time**: ~60 seconds (varies based on Suno's load)

⏱️ **API Calls**: Approximately 15-30 calls to check status

⏱️ **Network Bandwidth**: ~3-5MB download for typical 3-minute song

⏱️ **Timeout Strategy**: 
- Total operation timeout: ~90 seconds
- Individual API call timeout: 60 seconds

## Integration with OpenClaw

This skill integrates with OpenClaw's skill framework:

- **Input**: OpenClaw parameters dictionary
- **Output**: Standard result dictionary with status and data
- **Error Handling**: All errors return proper error status and messages

## Workflow Integration

This skill works best with:

1. **ChatGPT Prompt Generator** → Generates the prompt
2. **Suno Music Generator** → Creates the music (this skill)
3. **Music Orchestrator** → Automates the complete pipeline

## Limitations

⚠️ **Generation Time**: Music generation takes ~60 seconds, not instant

⚠️ **API Limits**: Suno AI has rate limits - check your API quota

⚠️ **File Size**: Generated files may be 3-10MB depending on length

⚠️ **URL Expiration**: Download URLs may expire after a period - save files promptly

## Support

For issues or questions:
1. Check the error messages and logs
2. Verify environment variables are set correctly
3. Ensure your Suno API key is valid
4. Check Suno API status at console.suno.ai
5. Review polling settings if generations timeout frequently
