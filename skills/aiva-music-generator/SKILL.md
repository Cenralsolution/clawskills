# AIVA Music Generator Skill

## Overview

This OpenClaw skill generates professional-grade music using **AIVA (Artificial Intelligence Virtual Artist)**, a leading AI music generation platform trusted by film composers, game developers, and content creators worldwide.

**AIVA** specializes in generating high-quality orchestral and cinematic music with precise control over genre, mood, tempo, and musical key. Perfect for films, games, podcasts, and content creation.

### Key Features

- 🎼 **Professional Quality**: Orchestral and cinematic compositions
- 🎯 **Full Control**: Genre, mood, tempo, and key specification
- ⚡ **Fast Generation**: Music generated within minutes
- 📥 **Auto-Download**: Automatically saves generated audio locally
- 🔒 **Secure**: API key-based authentication, no credentials exposed
- 📊 **Detailed Metadata**: Complete composition information included

### Strengths vs. Alternatives

| Feature | AIVA | Mubert | Replicate | Soundraw |
|---------|------|--------|-----------|----------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Genres | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Orchestral | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Control | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| API Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Documentation | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**AIVA is recommended for**: Film/TV scores, cinematic video content, orchestral compositions, professional game soundtracks

---

## Installation

### 1. Set Up AIVA Account

```bash
# Visit AIVA website
https://www.aiva.ai

# Sign up for a free or premium account
# Free tier includes test credits
# Paid plans: Creator ($9.99/mo), Pro ($49.99/mo), Studio ($199.99/mo)
```

### 2. Get API Key

```bash
# 1. Log in to your AIVA account
# 2. Go to Settings → API or Developer Dashboard
# 3. Click "Generate API Key" or copy existing key
# 4. Copy the key (format: 64-character hex string)
```

### 3. Configure Environment

```bash
# Set the environment variable
export AIVA_API_KEY="your-api-key-here"

# Optional: Set custom output directory
export MUSIC_OUTPUT_DIR="./generated_music"
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

The skill requires:
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `pyyaml` - Configuration file parsing

---

## Usage

### Basic Usage

```python
from aiva_music_generator.skill import AIVAMusicGenerator

# Initialize the skill
generator = AIVAMusicGenerator()

# Generate music
result = generator.generate_music(
    prompt="orchestral theme with dramatic strings",
    duration=60,
    genre="orchestral",
    mood="epic",
    tempo=120,
    key="D major"
)

print(f"Music saved to: {result['file_path']}")
print(f"Download URL: {result['audio_url']}")
```

### Using with OpenClaw Framework

```python
# In your OpenClaw skill implementation
from aiva_music_generator.skill import AIVAMusicGenerator

skill = AIVAMusicGenerator()

output = skill.execute_skill({
    "prompt": "epic orchestral theme for movie trailer",
    "duration": 45,
    "genre": "orchestral",
    "mood": "epic",
    "tempo": 100,
    "key": "G major"
})

if output["status"] == "success":
    print(f"Generated: {output['data']['file_path']}")
```

### Advanced Configuration

```python
result = generator.generate_music(
    prompt="ambient electronic with pads and atmospheric effects",
    duration=120,  # 2 minutes
    genre="electronic",
    mood="mysterious",
    tempo=70,
    key="A minor",
    polling_interval=3,  # Check status every 3 seconds
    max_wait_time=600    # Wait up to 10 minutes
)
```

### Parameter Guide

#### Prompt (Required)
- **Type**: String, 10-500 characters
- **Purpose**: Text description of the music you want
- **Tips**:
  - Be specific about instruments: "with strings and piano"
  - Describe the mood: "melancholic, introspective"
  - Mention intended use: "for dramatic film scene"
  - Include tempo suggestions: "slow, contemplative"

**Good Examples**:
- "Orchestral arrangement with full strings section, French horns, and brass for epic fantasy battle scene"
- "Minimalist piano piece, simple melody, peaceful and meditative atmosphere"
- "Jazz trio: piano, upright bass, drums - upbeat and playful"

**Avoid**:
- Vague descriptions like "good music" or "nice song"
- Very long descriptions (over 500 chars)
- Requesting copyrighted songs explicitly

#### Duration
- **Type**: Integer (15-120 seconds)
- **Default**: 30 seconds
- **Note**: Longer durations take more time, longer durations may cost more credits

#### Genre
Available genres:
- `ambient` - Atmospheric, background music
- `orchestral` - Classical orchestra arrangements
- `electronic` - Synthesized, digital music
- `jazz` - Jazz ensembles and styles
- `classical` - Traditional classical compositions
- `rock` - Rock band arrangements
- `pop` - Popular music styles
- `cinematic` - Film score style
- `games` - Video game music
- `electronic_dance` - EDM and dance music

#### Mood
Available moods:
- `calm` - Peaceful, relaxing
- `energetic` - Upbeat, dynamic
- `dark` - Mysterious, intense
- `happy` - Joyful, positive
- `melancholic` - Sad, introspective
- `epic` - Grand, dramatic
- `mysterious` - Enigmatic, suspenseful
- `romantic` - Emotional, tender

#### Tempo
- **Type**: Integer (40-240 BPM)
- **Default**: 90 BPM
- **Reference**:
  - 40-60 BPM: Slow, funeral march pace
  - 61-80 BPM: Ballad, lullaby
  - 81-120 BPM: Walking, moderate pace
  - 121-156 BPM: Energetic, dancing
  - 157-240 BPM: Fast, frantic

#### Key
- **Type**: String
- **Default**: "C major"
- **Available Keys**: C, D, E, F, G, A, B (both major and minor)
- **Musical Knowledge**: Different keys evoke different moods
  - C major: Fresh, cheerful
  - A minor: Dark, introspective
  - G major: Bright, triumphant
  - D minor: Serious, dramatic

---

## Output

### Response Structure

```json
{
  "composition_id": "comp_abc123xyz789",
  "generation_id": "gen_def456uvw012",
  "audio_url": "https://api.aiva.ai/v1/download/audio_abc123",
  "file_path": "/path/to/aiva_comp_abc123xyz789_20260215_143022.wav",
  "status": "completed",
  "duration": 60,
  "genre": "orchestral",
  "mood": "epic",
  "timestamp": "2026-02-15T14:30:22.123456",
  "metadata": {
    "prompt": "orchestral theme with dramatic strings and brass",
    "tempo": 120,
    "key": "D major",
    "model": "AIVA",
    "file_size": 2457600
  }
}
```

### File Formats

- **Format**: WAV (lossless) or MP3 (compressed)
- **Sample Rate**: 44.1 kHz (CD quality)
- **Bit Depth**: 16-bit
- **File Size**: ~2-5 MB per minute depending on format
- **Location**: Saved to `MUSIC_OUTPUT_DIR` environment variable

---

## API Endpoints

### Core Endpoints Used

```
POST   /compositions              - Create a composition
POST   /compositions/{id}/generate - Trigger generation
GET    /generations/{id}/status   - Check generation status
GET    /audio/download            - Download generated audio
```

### Rate Limits

**Free Tier**:
- 10 generations per month
- 30-second generation limit
- Standard quality

**Creator Plan** ($9.99/month):
- 100 generations per month
- 2-minute generation limit
- High quality

**Pro Plan** ($49.99/month):
- 1,000 generations per month
- Full features
- Priority processing

**Studio Plan** ($199.99/month):
- Unlimited generations
- Commercial license
- Priority support

Check your AIVA dashboard for actual limits and remaining quota.

---

## Error Handling

### Common Errors and Solutions

#### InvalidAPIKey
```
Error: Invalid API Key
```
**Solution**:
1. Verify `AIVA_API_KEY` environment variable is set
2. Check API key is correct (copy from dashboard, not partially)
3. Ensure no extra whitespace in key
4. Generate new key if needed

#### QuotaExceeded
```
Error: API quota exceeded. You have 0 remaining generations.
```
**Solution**:
1. Check your AIVA subscription tier
2. Upgrade to a higher plan if needed
3. Wait until next billing period for free tier
4. Usage details available in AIVA dashboard

#### InvalidPrompt
```
Error: Prompt does not meet requirements
```
**Solution**:
1. Ensure prompt is 10-500 characters
2. Make description more specific
3. Remove special characters if present
4. Try a simpler prompt

#### GenerationTimeout
```
Error: Generation did not complete within 300 seconds
```
**Solution**:
1. Increase `max_wait_time` parameter (up to 600 seconds)
2. Try with shorter `duration` (30-60 seconds)
3. Simplify the prompt
4. Try again, may be temporary API load

#### TimeoutError
```
Error: Connection timeout
```
**Solution**:
1. Check internet connection
2. Try again after a few seconds
3. Check AIVA service status: https://status.aiva.ai
4. If persistent, contact AIVA support

---

## Performance Considerations

### Generation Time

**Typical Generation Times**:
- 15-30 seconds: 1-3 minutes
- 31-60 seconds: 3-8 minutes
- 61-120 seconds: 8-15 minutes

**Factors Affecting Speed**:
- Current AIVA API load
- Your subscription tier (paid plans prioritized)
- Complexity of prompt
- Server location

### Cost Calculation

**Free Tier**:
- 10 compositions/month
- ~0.10 per composition

**Creator Tier** ($9.99/month):
- 100 compositions/month
- ~$0.10 per composition

**Pro Tier** ($49.99/month):
- 1,000 compositions/month
- ~$0.05 per composition

---

## Integration with OpenClaw Skills

### Chaining with ChatGPT Prompt Generator

```python
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from aiva_music_generator.skill import AIVAMusicGenerator

# Generate prompt from theme
prompt_gen = ChatGPTPromptGenerator()
prompt_result = prompt_gen.generate_prompt(theme="cyberpunk")

# Use prompt to generate music
music_gen = AIVAMusicGenerator()
music_result = music_gen.generate_music(
    prompt=prompt_result["detailed_prompt"],
    genre=prompt_result["suggested_genre"],
    mood=prompt_result["suggested_mood"]
)

print(f"Generated: {music_result['file_path']}")
```

### With Music Orchestrator

The **Music Generation Orchestrator** skill automatically handles:
1. Getting prompt from ChatGPT Prompt Generator
2. Generating music with AIVA
3. Managing outputs and metadata
4. Error handling across both skills

---

## Security and Privacy

### Data Handling

- ✅ API keys stored in environment variables, never hardcoded
- ✅ Prompts sent to official AIVA API only
- ✅ All communications use HTTPS/TLS encryption
- ✅ No user data stored locally except generated audio files
- ✅ Audio files stored locally with restricted permissions (mode 0600)

### API Key Security

```bash
# GOOD: Using environment variable
export AIVA_API_KEY="your-key"
python your_script.py

# BAD: Hardcoding key
api_key = "your-key"  # Don't do this!

# ALSO BAD: Committing to git
git add config.py  # If it contains key
```

### Recommendations

1. **Rotate keys periodically** (every 90 days)
2. **Use environment variables** or secure vaults
3. **Don't share keys** via email, chat, or version control
4. **Monitor AIVA dashboard** for unusual activity
5. **Test keys** in non-production first

---

## Troubleshooting

### Skill Not Generating Music

**Symptom**: `execute_skill()` returns immediately with no results

**Diagnosis**:
```python
try:
    result = generator.generate_music(
        prompt="test",
        duration=30
    )
except Exception as e:
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
```

**Solutions**:
1. Check API key: `echo $AIVA_API_KEY`
2. Check internet connection: `ping api.aiva.ai`
3. Check AIVA service status: https://status.aiva.ai
4. Review logs: Check console output for errors

### File Not Saving

**Symptom**: Generation succeeds but file not created

**Check**:
```bash
# Verify output directory exists and is writable
ls -la $MUSIC_OUTPUT_DIR
chmod 755 $MUSIC_OUTPUT_DIR

# Check disk space
df -h
```

**Solution**:
1. Create directory: `mkdir -p $MUSIC_OUTPUT_DIR`
2. Set permissions: `chmod 755 $MUSIC_OUTPUT_DIR`
3. Free disk space if full
4. Check that MUSIC_OUTPUT_DIR path is valid

### API Key Not Found

**Error**:
```
KeyError: AIVA_API_KEY not found in environment
```

**Solution**:
```bash
# Check if set
echo $AIVA_API_KEY

# If empty, set it
export AIVA_API_KEY="your-key-from-dashboard"

# Or in .env file
echo "AIVA_API_KEY=your-key" > .env
```

### Generation Hangs

**Symptom**: Script hangs at polling stage

**Solution**:
```python
# Use smaller timeout for testing
result = generator.generate_music(
    prompt="test",
    max_wait_time=60  # Only wait 1 minute
)

# Or manually set polling interval
result = generator.generate_music(
    prompt="test",
    polling_interval=5  # Check every 5 seconds
)
```

---

## Debugging

Enable detailed logging:

```python
import logging

# Set logging to DEBUG
logging.basicConfig(level=logging.DEBUG)

# Now run generation - will show all API calls
generator = AIVAMusicGenerator()
result = generator.generate_music("test prompt", duration=30)
```

Check error logs:
```bash
# View recent API calls
grep "AIVA" your_app.log | tail -20

# See polling details
grep "Poll" your_app.log
```

---

## Support

- **AIVA Documentation**: https://www.aiva.ai/api
- **AIVA Support**: https://www.aiva.ai/contact
- **Status Page**: https://status.aiva.ai
- **Community**: Discord channel on AIVA website

---

## Version History

### v1.0.0 - Initial Release (2026-02-15)
- ✨ Full AIVA API integration
- 🎼 Support for all genres and moods
- 📥 Auto-download of generated audio
- 🔒 Secure API key handling
- 📊 Comprehensive metadata tracking
- ✅ Production-ready code

---

## License

This skill is part of the OpenClaw Skills Platform. See main LICENSE file for terms.

Generated audio files are subject to AIVA's Terms of Service. Verify commercial usage rights match your AIVA plan.
