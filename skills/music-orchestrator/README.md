# Music Generation Orchestrator Skill

## Overview

This skill orchestrates the complete music generation pipeline. It takes a theme or topic and automatically:
1. Generates a detailed music prompt using ChatGPT
2. Generates music from that prompt using Suno AI
3. Returns a direct download link to the music file

This is the end-to-end skill - users only need to provide a theme!

## Features

✅ **Complete Pipeline** - Automates the entire workflow from theme to downloadable music

✅ **Intelligent Orchestration** - Manages dependencies and error handling across multiple services

✅ **ChainedExecution** - Seamlessly passes data between ChatGPT and Suno AI

✅ **Detailed Workflow Reporting** - Returns complete workflow execution details for transparency

✅ **Robust Error Handling** - Handles errors at any stage with clear error messages

✅ **Security-First Design** - All API keys and sensitive data protected

## Usage

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `theme` | string | Yes | Music theme or topic (e.g., "cyberpunk city", "tropical beach sunset") |
| `tags` | string | No | Optional tags for Suno AI (max 200 characters) |

### Output

```json
{
  "status": "success",
  "theme": "tropical beach sunset with ocean waves",
  "download_url": "https://cdn.suno.ai/music/song_xyz789.mp3",
  "song_id": "song_xyz789",
  "workflow": {
    "step1_prompt_generation": {
      "status": "complete",
      "generated_prompt": "Create a relaxing tropical ambient track that captures the golden hues and gentle waves of a sunset beach...",
      "model": "gpt-4",
      "tokens_used": 142
    },
    "step2_music_generation": {
      "status": "complete",
      "metadata": {
        "title": "Tropical Sunset Dreams",
        "duration": 180,
        "created_at": "2026-02-15T15:45:30Z",
        "tags": "ambient,tropical,relaxing"
      }
    }
  },
  "timestamp": "2026-02-15T15:46:15.123Z"
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set All Required Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4"

# Suno AI Configuration
export SUNO_API_KEY="your-suno-api-key"
export SUNO_API_BASE_URL="https://api.suno.ai"
export SUNO_MAX_RETRIES="30"
export SUNO_RETRY_DELAY="2"
```

### 3. Configuration

The orchestrator uses the individual skill configuration files:
- `../chatgpt-prompt-generator/config.yaml`
- `../suno-music-generator/config.yaml`

## How It Works

### Workflow Steps

#### Step 1: Generate Music Prompt (ChatGPT)
- **Input**: User's theme/topic
- **Processing**: ChatGPT creates a detailed, creative music prompt
- **Output**: Structured music generation prompt
- **Error Handling**: Returns error if prompt generation fails

#### Step 2: Generate Music (Suno AI)
- **Input**: Generated prompt from Step 1
- **Processing**: Suno AI generates the actual music file
- **Polling**: Waits for generation to complete (up to 90 seconds)
- **Output**: Download link and metadata
- **Error Handling**: Returns error if music generation fails

### Complete Execution Flow

```
User provides theme
    ↓
Validate theme
    ↓
Call ChatGPT Prompt Generator
    ├─ Success → Continue to Step 2
    └─ Error → Return error to user
    ↓
Call Suno AI Music Generator
    ├─ Success → Return download link
    └─ Error → Return error with partial data
    ↓
Return complete result with workflow details
```

## Error Handling

The orchestrator handles errors at each step:

### Step 1 Errors (Prompt Generation)
- Theme validation fails
- ChatGPT API authentication fails
- ChatGPT API rate limit exceeded
- ChatGPT API timeout
- Unexpected ChatGPT error

### Step 2 Errors (Music Generation)
- Prompt is invalid for Suno
- Suno API authentication fails
- Music generation times out
- Suno API error
- Unexpected Suno error

All errors include:
- Clear error message
- Error type classification
- Original input data (where appropriate)
- Timestamp for debugging

## Security Considerations

🔒 **Multiple API Keys**
- Both OpenAI and Suno API keys stored securely
- Never appear in logs or error messages
- Environment variables are the only secure method

🔒 **Data Flow**
- Theme is validated before processing
- Generated prompt is sanitized
- All inter-service communication is HTTPS
- No sensitive data persisted

🔒 **Error Messages**
- User-friendly without exposing internals
- Technical details logged securely
- External API errors are sanitized

## Performance Characteristics

⏱️ **Expected Total Time**: ~90 seconds
- ChatGPT prompt generation: ~3-5 seconds
- Suno music generation: ~60 seconds
- Polling overhead: ~20-25 seconds

⏱️ **API Calls**:
- 1 call to ChatGPT API
- ~15-30 calls to Suno API (polling)

⏱️ **Network Data**:
- Upload: <1KB
- Download: 3-10MB (music file)

## Testing

### Quick Test

```python
from skill import execute_skill

result = execute_skill({
    "theme": "rainy evening in the city"
})

if result['status'] == 'success':
    print(f"✅ Download music at: {result['download_url']}")
else:
    print(f"❌ Error: {result['message']}")
```

### Test with Tags

```python
result = execute_skill({
    "theme": "morning coffee",
    "tags": "chill,lo-fi,peaceful"
})
```

### Manual Step Testing

You can test individual steps:

```python
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from suno_music_generator.skill import SunoAIMusicGenerator

# Step 1: Generate prompt
generator = ChatGPTPromptGenerator()
prompt_result = generator.generate_prompt("space exploration")
print(f"Generated Prompt: {prompt_result['prompt']}")

# Step 2: Generate music
music_gen = SunoAIMusicGenerator()
music_result = music_gen.generate_music(prompt_result['prompt'])
print(f"Music URL: {music_result['file_url']}")
```

## Integration with OpenClaw

The orchestrator integrates seamlessly with OpenClaw:

- **Single Entry Point**: Just call the orchestrator, it manages everything
- **Standard Interface**: Follows OpenClaw skill framework conventions
- **Dependency Management**: Automatically initializes dependent skills
- **Error Propagation**: All errors properly formatted for OpenClaw error handling
- **Audit Trail**: Complete workflow logged for debugging

## Usage Examples

### Example 1: Generate Ambient Music

```python
result = execute_skill({
    "theme": "peaceful meditation garden with flowing water"
})
# Returns: Download link to ambient meditation music
```

### Example 2: Generate Dance Music with Tags

```python
result = execute_skill({
    "theme": "summer beach party",
    "tags": "dance,electronic,upbeat,summer"
})
# Returns: Download link to dance music
```

### Example 3: Generate Cinematic Music

```python
result = execute_skill({
    "theme": "epic fantasy battle scene with dragons"
})
# Returns: Download link to cinematic music
```

## Workflow Transparency

The orchestrator returns detailed workflow information:

```json
"workflow": {
  "step1_prompt_generation": {
    "status": "complete",
    "generated_prompt": "...",
    "model": "gpt-4",
    "tokens_used": 145
  },
  "step2_music_generation": {
    "status": "complete",
    "metadata": {
      "title": "...",
      "duration": 180,
      "created_at": "...",
      "tags": "..."
    }
  }
}
```

This allows users and debuggers to understand exactly what happened at each step.

## Limitations & Considerations

⚠️ **Generation Time**: Not instant - takes ~90 seconds total

⚠️ **API Quotas**: Both OpenAI and Suno have rate limits and quotas

⚠️ **File Hosting**: Music files hosted by Suno, URLs may expire

⚠️ **Theme Interpretation**: Output quality depends on theme clarity

⚠️ **Sequential Processing**: Steps run sequentially (cannot parallelize)

## Troubleshooting

### "OPENAI_API_KEY not found"
- Solution: Export the environment variable: `export OPENAI_API_KEY="your-key"`

### "SUNO_API_KEY not found"
- Solution: Export the environment variable: `export SUNO_API_KEY="your-key"`

### "Music generation timed out"
- Suno API is slow or overloaded
- Solution: Wait a moment and try again, or increase `SUNO_MAX_RETRIES`

### "Rate limit exceeded"
- Too many requests to OpenAI or Suno
- Solution: Wait a few minutes before trying again

### "Theme contains invalid characters"
- Theme has special characters not allowed
- Solution: Stick to letters, numbers, spaces, hyphens, and commas

## Support & Feedback

For issues:
1. Check error messages in the returned result
2. Verify all environment variables are set
3. Check API status pages:
   - OpenAI: https://status.openai.com/
   - Suno: https://www.suno.ai/
4. Review the individual skill READMEs for detailed information

## Next Steps

After generating music:
1. Download the file from the provided URL
2. Test the music quality
3. Use in your application or content
4. Provide feedback on theme-to-music quality

For customization:
1. Modify the ChatGPT system prompt for different music styles
2. Adjust Suno settings for different music lengths/styles
3. Add intermediate processing steps as needed
