# Mubert Music Generator Skill

## Overview

This OpenClaw skill generates royalty-free music using **Mubert API**. Mubert specializes in fast, affordable AI-generated music with extensive style control and built-in commercial licensing.

**Mubert** is perfect for content creators, streamers, podcasters, and businesses needing quick, high-quality background music with commercial rights included.

### Key Features

- 🎵 **23+ Styles**: Diverse genre coverage from ambient to metal
- 🏷️ **Mood Tags**: Precise emotional control
- ⚡ **Fast Generation**: Music ready in 10-30 seconds
- 💰 **Affordable**: Lower cost than alternatives
- 📄 **Commercial License**: Included in all plans
- 📥 **Auto-Download**: Saves to local directory
- 🔒 **Secure**: API key authentication, no credentials exposed

### Strengths

| Feature | Mubert | AIVA | Replicate | Soundraw |
|---------|--------|------|-----------|----------|
| Generation Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Style Options | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Affordability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Commercial License | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Mubert is recommended for**: Content creators, streamers, podcasters, agencies, businesses, YouTube channels

---

## Installation

### 1. Set Up Mubert Account

```bash
# Visit Mubert
https://mubert.com

# Sign up with email or social account
# Free tier available with limited generations per month
```

### 2. Get API Key

```bash
# 1. Log in to https://mubert.com
# 2. Go to Account → API or Developer Dashboard
# 3. Create or copy your API key
# 4. Copy the key
```

### 3. Configure Environment

```bash
# Set API key
export MUBERT_API_KEY="your-api-key-here"

# Optional: Custom output directory
export MUSIC_OUTPUT_DIR="./generated_music"
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Requires:
- `requests` - HTTP client
- `python-dotenv` - Environment variables
- `pyyaml` - Configuration files

---

## Usage

### Basic Usage

```python
from mubert_music_generator.skill import MubertMusicGenerator

# Initialize
generator = MubertMusicGenerator()

# Generate music
result = generator.generate_music(
    style="ambient",
    duration=120,
    mood="relaxing",
    intensity=3
)

print(f"Generated: {result['file_path']}")
```

### Using with Moods

```python
result = generator.generate_music(
    style="lo_fi",
    duration=300,  # 5 minutes
    mood="happy",
    intensity=4
)
```

### With Text Description

```python
result = generator.generate_music(
    style="electronic",
    duration=60,
    mood="energetic",
    text="upbeat with heavy bass and synths",
    intensity=8
)
```

### Intensity Control

```python
# Calm, subtle music
result = generator.generate_music(
    style="jazz",
    mood="calm",
    intensity=2  # Very subtle
)

# Energetic, prominent music
result = generator.generate_music(
    style="deep_house",
    mood="energetic",
    intensity=9  # Very intense
)
```

### Available Styles

23+ styles available:
- ambient, electronic, lo_fi, cinematic, chillhop
- synthwave, indie, rock, hip_hop, jazz
- classical, folk, pop, trap, tropical
- deep_house, techno, trance, dubstep
- metal, vocal, soul, reggae

### Available Moods

- relaxing, energetic, happy, sad, dark
- aggressive, calm, uplifting, melancholic, cute

---

## Parameter Guide

#### Style (Required)
- **Type**: String
- **Options**: 23 styles (see list above)
- **Examples**:
  - "ambient" - Atmospheric background
  - "lo_fi" - Lo-fi hip-hop
  - "cinematic" - Film score style
  - "electronic" - Synthesized music
  - "jazz" - Jazz ensemble

#### Duration
- **Type**: Integer (10-600 seconds)
- **Default**: 60 seconds
- **Note**: Longer duration = more credits

#### Mood
- **Type**: String (optional)
- **Options**: calm, energetic, happy, sad, dark, aggressive, etc.
- **Purpose**: Add emotional tone

#### Text
- **Type**: String (optional, max 100 chars)
- **Purpose**: Additional description for enhanced generation
- **Example**: "upbeat with heavy bass and synths"

#### Intensity
- **Type**: Integer (0-10)
- **Default**: 5
- **Low (0-3)**: Subtle, background
- **Medium (4-6)**: Balanced
- **High (7-10)**: Prominent, intense

---

## Output

### Response Structure

```json
{
  "track_id": "tr_abc123xyz789",
  "download_url": "https://api.mubert.com/track/download/abc123",
  "status": "completed",
  "duration": 120,
  "style": "ambient",
  "file_path": "/path/to/mubert_tr_abc123_20260215_143022.wav",
  "timestamp": "2026-02-15T14:30:22.123456",
  "metadata": {
    "mood": "relaxing",
    "intensity": 3,
    "model": "Mubert",
    "file_size": 4915200
  }
}
```

### Audio Files

- **Format**: WAV (lossless)
- **Sample Rate**: 44.1 kHz
- **Channels**: Stereo
- **File Size**: ~1 MB per 30 seconds
- **License**: Royalty-free, commercial use allowed

---

## Pricing

### Subscription Tiers

**Free Tier**:
- Limited generations per month
- Personal use only
- ~0.10 per composition

**Creator Plan** ($9.99/month):
- 100 generations/month
- Commercial license included
- ~$0.10 per composition

**Pro Plan** ($49.99/month):
- 1,000+ generations/month
- Priority processing
- ~$0.05 per composition

**Custom Plans**:
- Unlimited generations
- Dedicated support
- Contact sales

Check [mubert.com/pricing](https://mubert.com/pricing) for current rates.

---

## Integration Examples

### With ChatGPT Prompt Generator

```python
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from mubert_music_generator.skill import MubertMusicGenerator

# Generate prompt for a theme
prompt_gen = ChatGPTPromptGenerator()
prompt_result = prompt_gen.generate_prompt(theme="cyberpunk")

# Use with Mubert
music_gen = MubertMusicGenerator()

# Extract style and mood from prompt
result = music_gen.generate_music(
    style="electronic",
    mood="dark",
    intensity=8,
    text=prompt_result["detailed_prompt"][:100]
)
```

### Batch Generation

```python
styles = ["ambient", "electronic", "lo_fi", "jazz"]
moods = ["calm", "energetic", "happy"]

generator = MubertMusicGenerator()
results = []

for style in styles:
    for mood in moods:
        result = generator.generate_music(
            style=style,
            mood=mood,
            duration=60
        )
        results.append(result)

print(f"Generated {len(results)} tracks")
```

---

## Error Handling

### Common Errors

#### Invalid API Key
```
Error: Invalid API key
```
**Solution**:
1. Check: `echo $MUBERT_API_KEY`
2. Verify in Mubert dashboard
3. Generate new key if needed

#### Quota Exceeded
```
Error: Quota exceeded for this month
```
**Solution**:
1. Upgrade subscription plan
2. Wait until next billing cycle
3. Check usage in dashboard

#### Invalid Style
```
Error: Unknown style 'xyz'
```
**Solution**:
Use `MubertMusicGenerator.list_styles()` to see available styles

#### Generation Timeout
```
Error: Generation did not complete
```
**Solution**:
1. Try with shorter duration (30s vs 120s)
2. Increase `max_wait_time`: `max_wait_time=120`
3. Try again - may be temporary API load

---

## Troubleshooting

### File Not Saving

**Check disk space and permissions**:
```bash
# Check output directory
ls -la $MUSIC_OUTPUT_DIR

# Create if missing
mkdir -p $MUSIC_OUTPUT_DIR

# Fix permissions
chmod 755 $MUSIC_OUTPUT_DIR
```

### Generation Takes Too Long

**Mubert is fast** - if generation is slow:
1. Check API status: https://mubert.com/status
2. Try simpler parameters (shorter duration)
3. Check internet connection
4. Retry after a few seconds

### Audio Quality Issues

- **Too quiet**: Use higher `intensity` (7-10)
- **Too loud**: Use lower `intensity` (1-3)
- **Wrong mood**: Different styles work better with specific moods
- **Try other styles**: Each style has different generation characteristics

---

## Best Practices

### For Streaming/Content

```python
# Background music for videos
result = generator.generate_music(
    style="lo_fi",
    duration=600,  # 10 minutes
    mood="calm",
    intensity=3
)
```

### For YouTube

```python
# Royalty-free guaranteed
result = generator.generate_music(
    style="cinematic",
    duration=120,
    mood="epic",
    intensity=8
)
# Use commercially - no attribution needed
```

### For Podcasts

```python
# Intro/outro music
result = generator.generate_music(
    style="pop",
    duration=15,
    mood="uplifting",
    intensity=7
)

# Transition music
result = generator.generate_music(
    style="ambient",
    duration=10,
    mood="calm",
    intensity=2
)
```

---

## Advanced Features

### List Available Styles

```python
styles = MubertMusicGenerator.list_styles()
print(styles)
```

### List Available Moods

```python
moods = MubertMusicGenerator.list_moods()
print(moods)
```

### Execute as Skill

```python
output = generator.execute_skill({
    "style": "ambient",
    "duration": 60,
    "mood": "relaxing",
    "intensity": 3
})

if output["status"] == "success":
    print(output["data"]["file_path"])
```

---

## Security

- ✅ API keys in environment variables only
- ✅ HTTPS encryption for all API calls
- ✅ No credentials stored in code or version control
- ✅ Audio files saved with restricted permissions (0600)
- ✅ No retry logging of sensitive data

### Token Safety

```bash
# GOOD: Environment variable
export MUBERT_API_KEY="..."
python script.py

# BAD: Hardcoded
api_key = "..."  # Never!

# ALSO BAD: Version control
git add config.py  # If contains key
```

---

## Version History

### v1.0.0 - Initial Release (2026-02-15)
- ✨ Full Mubert API integration
- 🎵 Support for 23+ styles
- 🏷️ Mood and intensity control
- 📥 Auto-download to local directory
- 🔒 Secure API key handling
- ✅ Production-ready

---

## Support

- **Mubert Website**: https://mubert.com
- **API Docs**: https://mubert.com/en/api
- **Support**: support@mubert.com
- **Status**: https://mubert.com/status

---

## License

Part of OpenClaw Skills Platform. See main LICENSE.

Generated music is royalty-free with commercial license included for all plans.
