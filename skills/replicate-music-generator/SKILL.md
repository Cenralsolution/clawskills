# Replicate Music Generator Skill

## Overview

This OpenClaw skill generates music using **Replicate**, a platform that hosts various AI models including Meta's **MusicGen**, Stability AI's **Stable Audio**, and other cutting-edge audio generation models.

**Replicate** offers flexibility through multiple model options and excellent API documentation, making it ideal for developers who want options and fine-grained control.

### Key Features

- 🎼 **Multiple Models**: Choose between MusicGen, MusicGen Large, Stable Audio, etc.
- 📊 **Fine-grained Control**: Temperature, top-k, top-p parameters for customization
- ⚡ **Fast Generation**: Async API with webhook support
- 📥 **Auto-Download**: Automatically saves generated audio locally
- 🔒 **Secure**: Token-based authentication, HTTPS encrypted
- 📈 **Pay-as-you-go**: Only pay for what you use with GPU time billing

### Comparison With Other Providers

| Feature | Replicate | AIVA | Mubert | Soundraw |
|---------|-----------|------|--------|----------|
| Model Selection | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Control Parameters | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| API Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Documentation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Cost / Credit | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Unlimited Plans | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Replicate is recommended for**: Developers, technical users wanting model flexibility, experimentation, research projects

---

## Installation

### 1. Set Up Replicate Account

```bash
# Visit Replicate
https://replicate.com

# Sign up with email or GitHub
# Free account includes $5 trial credit
```

### 2. Get API Token

```bash
# 1. Log in to https://replicate.com
# 2. Go to Account → API Tokens
# 3. Click "Create token"
# 4. Copy the token (format: r8_xxxxx...)
```

### 3. Configure Environment

```bash
# Set the API token
export REPLICATE_API_TOKEN="r8_..."

# Optional: Set output directory
export MUSIC_OUTPUT_DIR="./generated_music"
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Requires:
- `requests` - HTTP client
- `python-dotenv` - Environment management
- `pyyaml` - Configuration parsing

---

## Usage

### Basic Usage

```python
from replicate_music_generator.skill import ReplicateMusicGenerator

# Initialize with default model (MusicGen)
generator = ReplicateMusicGenerator()

# Generate music
result = generator.generate_music(
    prompt="upbeat electronic dance music with deep bass",
    duration=30,
    temperature=0.95,
    top_k=250,
    top_p=0.0
)

print(f"Generated: {result['file_path']}")
```

### Using Different Models

```python
# Use MusicGen Large (improved quality)
generator = ReplicateMusicGenerator(model="musicgen-large")

result = generator.generate_music(
    prompt="orchestral theme with dramatic strings",
    duration=30,
    temperature=0.8
)
```

### Available Models

#### MusicGen (Default)
```python
generator = ReplicateMusicGenerator(model="musicgen")
```
- Best quality text-to-music
- Diverse genre support
- 5-30 second generation

#### MusicGen Large
```python
generator = ReplicateMusicGenerator(model="musicgen-large")
```
- Improved quality over base model
- Better for complex arrangements
- Slightly slower generation

#### Stable Audio
```python
generator = ReplicateMusicGenerator(model="stable-audio")
```
- Stability AI's audio generation
- Better for sound effects
- Different generation characteristics

### Advanced Parameters

```python
result = generator.generate_music(
    prompt="calm ambient piano with reverb",
    duration=30,
    temperature=0.7,        # Less random: 0.7 vs default 1.0
    top_k=200,              # Reduced diversity
    top_p=0.9,              # Nucleus sampling enabled
    polling_interval=1,     # Check status every 1 second
    max_wait_time=300       # Wait up to 5 minutes
)
```

### Parameter Guide

#### Prompt (Required)
- **Type**: String, 5-500 characters
- **Purpose**: Text description of music
- **Tips**:
  - Specific instrumentation: "with piano and strings"
  - Mood: "melancholic and introspective"
  - Tempo hints: "slow tempo, 70 BPM"
  - Genre: "electronic with synth leads"

**Good Examples**:
- "Upbeat electronic dance music with heavy bass and synth leads"
- "Slow jazz ballad with mellow saxophone and walking bass"
- "Ambient drone with pad layers and reverb effects"

#### Duration
- **Type**: Integer (5-30 seconds)
- **Default**: 30 seconds
- **Note**: Longer = more credits

#### Temperature
- **Type**: Float (0.0-1.0)
- **Default**: 1.0
- **Effect**:
  - 0.0: Deterministic, same result every time
  - 0.5: Balanced - somewhat varied
  - 1.0: Maximum randomness/creativity

#### Top-K and Top-P
- **top_k**: Limits diversity (default 250)
- **top_p**: Nucleus sampling (default 0.0 = disabled)
- **Use Case**: Fine-tune generation diversity

---

## Output

### Response Structure

```json
{
  "prediction_id": "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx",
  "output_url": "https://replica-image-bucket.com/output.wav",
  "file_path": "/path/to/replicate_xxxxxxx_20260215_143022.wav",
  "status": "completed",
  "duration": 30,
  "model": "musicgen",
  "timestamp": "2026-02-15T14:30:22.123456",
  "metadata": {
    "prompt": "upbeat electronic dance music",
    "temperature": 0.95,
    "top_k": 250,
    "top_p": 0.0,
    "model_provider": "Replicate",
    "file_size": 2457600
  }
}
```

### File Formats

- **Format**: WAV (linear PCM)
- **Sample Rate**: 16 kHz or 24 kHz
- **Channels**: Mono
- **File Size**: ~500 KB - 1 MB per 30 seconds
- **Location**: `MUSIC_OUTPUT_DIR`

---

## Pricing

### Cost Model

Replicate uses **GPU time** billing:
- **MusicGen**: ~0.50 - 1.00 per 30-second generation
- **MusicGen Large**: ~1.00 - 2.00 per 30-second generation
- **Stable Audio**: ~0.50 per generation

### Free Trial

- **New Users**: $5 trial credit
- **Duration**: No expiration on trial credit
- **After**: Pay-as-you-go or upgrade to Pro plan

### Pro Plan

- **Cost**: $20/month
- **Includes**: Monthly credits for models
- **Rate Limits**: Higher concurrency

Check [replicate.com/pricing](https://replicate.com/pricing) for current rates.

---

## Error Handling

### Common Errors

#### Invalid API Token
```
Error: Invalid API token
```
**Solution**:
1. Check `REPLICATE_API_TOKEN` is set: `echo $REPLICATE_API_TOKEN`
2. Verify token format (starts with `r8_`)
3. Generate new token at https://replicate.com/account/api-tokens
4. Ensure token has no quotes or whitespace

#### Insufficient Credits
```
Error: You do not have enough credits
```
**Solution**:
1. Check account balance at replicate.com
2. Add payment method
3. Purchase additional credits
4. Or wait for monthly Pro credit reset

#### Model Not Found
```
Error: Version not found
```
**Solution**:
1. Check model name is correct
2. Model may have been updated - use latest version
3. See `list_available_models()` for working models

#### GenerationTimeout
```
Error: Prediction did not complete within 600 seconds
```
**Solution**:
1. Increase `max_wait_time` parameter
2. Try with shorter `duration`
3. Simplify prompt
4. Try again - may be temporary API load

---

## Integration with Other Skills

### Chain with ChatGPT Prompt Generator

```python
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from replicate_music_generator.skill import ReplicateMusicGenerator

# Generate prompt
prompt_gen = ChatGPTPromptGenerator()
prompt_result = prompt_gen.generate_prompt(theme="cyberpunk")

# Generate music with that prompt
music_gen = ReplicateMusicGenerator(model="musicgen")
music_result = music_gen.generate_music(
    prompt=prompt_result["detailed_prompt"],
    duration=30,
    temperature=0.8
)

print(f"Generated: {music_result['file_path']}")
```

### Use with Music Orchestrator

The **Music Generation Orchestrator** automatically handles:
1. Prompt generation
2. Music generation with Replicate
3. Download management
4. Error handling

```python
# Orchestrator automatically routes to Replicate
from music_orchestrator.skill import MusicOrchestrator

orchestrator = MusicOrchestrator(music_provider="replicate")
result = orchestrator.generate_music_from_theme("ambient")
```

---

## API Endpoints

### Replicate API

```
POST   /predictions           - Create a prediction (async)
GET    /predictions/{id}      - Get prediction status
POST   /predictions/{id}/cancel - Cancel running prediction
GET    /models/{owner}/{name} - Get model info
```

### Full Documentation

See https://replicate.com/docs for complete API reference and webhook support.

---

## Security and Privacy

### Data Handling

- ✅ API tokens stored in environment variables only
- ✅ Prompts sent to official Replicate API
- ✅ HTTPS/TLS encryption on all connections
- ✅ Generated audio saved locally with restricted permissions (0600)
- ✅ No user data retained by Replicate after generation

### Best Practices

```bash
# GOOD: Environment variable
export REPLICATE_API_TOKEN="r8_..."
python script.py

# BAD: Hardcoding
api_token = "r8_..."  # Don't do this!

# ALSO BAD: Git commit
git add secrets.py   # If it contains token
```

### Token Rotation

- Rotate tokens every 90 days
- Use environment variables
- Never commit tokens to version control
- Monitor API usage for suspicious activity

---

## Troubleshooting

### Generation Not Starting

**Symptom**: No prediction created

**Check**:
```python
try:
    result = generator.generate_music("test prompt")
except Exception as e:
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
```

**Solutions**:
1. Verify API token: `echo $REPLICATE_API_TOKEN`
2. Check internet connection
3. Check Replicate status: https://status.replicate.com
4. Verify credits available

### File Not Downloading

**Symptom**: Generation succeeds but no local file

**Check**:
```bash
ls -la $MUSIC_OUTPUT_DIR
df -h
```

**Solutions**:
1. Create directory: `mkdir -p $MUSIC_OUTPUT_DIR`
2. Check disk space
3. Verify directory is writable: `chmod 755 $MUSIC_OUTPUT_DIR`

### Prediction Never Completes

**Symptom**: Stuck in polling loop

**Solution**:
```python
# Use shorter timeout for debugging
result = generator.generate_music(
    "test",
    max_wait_time=60  # Only wait 1 minute
)

# Check status manually
import requests
response = requests.get(
    f"https://api.replicate.com/v1/predictions/{prediction_id}",
    headers={"Authorization": f"Token {api_token}"}
)
print(response.json())
```

---

## Debugging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

generator = ReplicateMusicGenerator()
result = generator.generate_music("test", duration=30)
```

### Check Recent Predictions

View your recent predictions at https://replicate.com/predictions

### API Request/Response

```python
# Replicate logs all API calls
# Check browser network tab or use:
import requests
requests.get("https://replicate.com/account/api-activity")
```

---

## Version History

### v1.0.0 - Initial Release (2026-02-15)
- ✨ Full Replicate API integration
- 🎼 Support for multiple models (MusicGen, MusicGen Large, Stable Audio)
- 🔧 Fine-grained parameter control
- 📥 Auto-download of generated audio
- 🔒 Secure token handling
- ✅ Production-ready

---

## Support

- **Replicate Docs**: https://replicate.com/docs
- **Replicate Status**: https://status.replicate.com
- **Support Email**: support@replicate.com
- **Community**: https://replicate.com/community

---

## License

Part of OpenClaw Skills Platform. See main LICENSE for terms.

Audio files are subject to Replicate's Terms of Service and the underlying model licenses (Meta, Stability AI, etc.).
