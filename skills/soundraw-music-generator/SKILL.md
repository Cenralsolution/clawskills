# Soundraw Music Generator Skill

## Overview

This OpenClaw skill generates original, customizable AI music using **Soundraw API**. Soundraw offers the most extensive customization options with 40+ moods, 20+ genres, and fine-grained instrumentation control.

**Soundraw** is ideal for creators wanting maximum control and customization over the generated music while maintaining royalty-free commercial licensing.

### Key Features

- 🎼 **Extensive Genres**: 20+ genres with full customization
- 😊 **40+ Moods**: Precise emotional tone selection
- 🎻 **Instrumentation Control**: Specify desired instruments
- 🎵 **Tempo Control**: Set exact BPM
- ⚡ **Energy Levels**: 1-10 energy scale
- 📄 **Commercial License**: Royalty-free for all uses
- 📥 **Auto-Download**: Saves to local directory

### Comparison

| Feature | Soundraw | AIVA | Replicate | Mubert |
|---------|----------|------|-----------|--------|
| Mood Options | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Customization | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Genre Variety | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Instrumentation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Soundraw is recommended for**: Professional composers, video producers, advertising agencies, musicians wanting maximum control

---

## Installation

### 1. Set Up Soundraw Account

```bash
# Visit Soundraw
https://www.soundraw.io

# Sign up with email or social account
# Free tier available for testing
```

### 2. Get API Key

```bash
# 1. Log in to https://www.soundraw.io
# 2. Go to Account Settings → API
# 3. Generate or copy your API key
# 4. Copy the key
```

### 3. Configure Environment

```bash
# Set API key
export SOUNDRAW_API_KEY="your-api-key-here"

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
from soundraw_music_generator.skill import SoundrawMusicGenerator

# Initialize
generator = SoundrawMusicGenerator()

# Generate music
result = generator.generate_music(
    genre="orchestral",
    mood="epic",
    duration=90,
    energy=8
)

print(f"Generated: {result['file_path']}")
```

### With Instrumentation

```python
result = generator.generate_music(
    genre="orchestral",
    mood="epic",
    duration=90,
    instrumentation="full orchestra with strings and brass",
    tempo=120,
    energy=8
)
```

### With Tempo

```python
# Slow, contemplative piece
result = generator.generate_music(
    genre="classical",
    mood="melancholic",
    duration=120,
    tempo=60,  # 60 BPM
    energy=3
)

# Fast, energetic piece
result = generator.generate_music(
    genre="electronic",
    mood="energetic",
    duration=60,
    tempo=140,  # 140 BPM
    energy=9
)
```

### Energy Control

```python
# Subtle background music
result = generator.generate_music(
    genre="ambient",
    mood="calm",
    energy=2  # Very subtle
)

# Prominent, intense music
result = generator.generate_music(
    genre="rock",
    mood="aggressive",
    energy=9  # Very intense
)
```

---

## Available Genres

20+ genres:
- ambient, acoustic, blues, classical, country
- dance, electronic, funk, hip_hop, jazz
- latin, metal, pop, punk, reggae
- rnb, rock, soul, world, cinematic
- experimental, indie

---

## Available Moods

40+ moods for precise emotional control:
- aggressive, angry, bright, calm, cheerful, cinematic, dark
- delicate, dramatic, dreamy, driven, emotional, energetic, epic
- ethereal, exploratory, gloomy, happy, hopeful, hypnotic, intense
- introspective, joyful, light, lonely, meditative, melancholic
- mellow, menacing, moody, mysterious, nostalgic, peaceful, playful
- proud, relaxed, romantic, sad, serene, sophisticated, tense
- uplifting, urgent, victorious, vintage

---

## Parameter Guide

#### Genre (Required)
- **Type**: String
- **Options**: 20 genres (see list above)
- **Examples**:
  - "orchestral" - With strings, brass
  - "electronic" - Synthesized
  - "classical" - Traditional
  - "ambient" - Atmospheric
  - "jazz" - Jazz ensemble

#### Mood (Required)
- **Type**: String
- **Options**: 40 moods (see list above)
- **Examples**:
  - "epic" - Grand, dramatic
  - "calm" - Peaceful, relaxing
  - "mysterious" - Enigmatic, suspenseful
  - "joyful" - Happy, uplifting
  - "melancholic" - Sad, introspective

#### Duration
- **Type**: Integer (10-600 seconds)
- **Default**: 60 seconds
- **Note**: Longer = more processing time, more credits

#### Instrumentation
- **Type**: String (optional)
- **Purpose**: Specify desired instruments
- **Examples**:
  - "full orchestra with strings and brass"
  - "acoustic guitar and piano"
  - "electronic synths and drums"
  - "solo violin with pad accompaniment"

#### Tempo
- **Type**: Integer (optional)
- **Units**: BPM (beats per minute)
- **Examples**:
  - 60 BPM: Slow, ballad pace
  - 90 BPM: Walking pace
  - 120 BPM: Upbeat, moderate
  - 140+ BPM: Fast, energetic

#### Energy
- **Type**: Integer (1-10)
- **Default**: 5 (balanced)
- **Low (1-3)**: Subtle, background
- **Medium (4-6)**: Balanced, moderate
- **High (7-10)**: Prominent, intense

---

## Output

### Response Structure

```json
{
  "track_id": "snd_abc123xyz789",
  "download_url": "https://api.soundraw.io/download/abc123",
  "status": "completed",
  "duration": 90,
  "genre": "orchestral",
  "mood": "epic",
  "file_path": "/path/to/soundraw_snd_abc123_20260215_143022.wav",
  "timestamp": "2026-02-15T14:30:22.123456",
  "metadata": {
    "instrumentation": "full orchestra",
    "tempo": 120,
    "energy": 8,
    "model": "Soundraw",
    "file_size": 7372800
  }
}
```

### Audio Files

- **Format**: WAV (high-quality lossless)
- **Sample Rate**: 44.1 kHz or 48 kHz
- **Channels**: Stereo
- **File Size**: ~1.5 MB per minute
- **License**: Royalty-free, commercial use allowed

---

## Pricing

### Subscription Plans

**Free Tier**:
- Limited generations per month
- Personal use
- Basic features

**Creator Plan** ($9.99/month):
- 50+ generations/month
- Commercial license
- Full customization

**Pro Plan** ($49.99/month):
- 500+ generations/month
- Priority processing
- Unlimited rendering

**Premium Plans**:
- Unlimited generations
- Direct support
- Custom arrangements

Check [soundraw.io/pricing](https://www.soundraw.io/pricing) for current rates.

---

## Integration Examples

### Professional Music for Video

```python
# Short cinematic intro
result = generator.generate_music(
    genre="cinematic",
    mood="epic",
    duration=15,
    tempo=100,
    energy=7,
    instrumentation="orchestral with strings and brass"
)

# Longer background score
result = generator.generate_music(
    genre="cinematic",
    mood="dramatic",
    duration=180,
    tempo=90,
    energy=6
)
```

### Background Music for Podcast

```python
# Intro
intro = generator.generate_music(
    genre="pop",
    mood="uplifting",
    duration=30,
    tempo=120,
    energy=7
)

# Transition
transition = generator.generate_music(
    genre="ambient",
    mood="calm",
    duration=10,
    tempo=80,
    energy=2
)

# Outro
outro = generator.generate_music(
    genre="pop",
    mood="satisfied",
    duration=30,
    tempo=110,
    energy=6
)
```

### With ChatGPT Prompt Generator

```python
from chatgpt_prompt_generator.skill import ChatGPTPromptGenerator
from soundraw_music_generator.skill import SoundrawMusicGenerator

# Generate prompt
prompt_gen = ChatGPTPromptGenerator()
prompt_result = prompt_gen.generate_prompt(theme="fantasy")

# Use for music generation
music_gen = SoundrawMusicGenerator()

# Parse mood/genre from prompt if needed
result = music_gen.generate_music(
    genre="orchestral",
    mood="epic",
    instrumentation=prompt_result.get("instrumentation", "orchestra"),
    duration=90,
    energy=8
)
```

---

## Advanced Features

### List Available Genres

```python
genres = SoundrawMusicGenerator.list_genres()
print(genres)  # 20 genres
```

### List Available Moods

```python
moods = SoundrawMusicGenerator.list_moods()
print(moods)  # 40 moods
```

### Get Skill Info

```python
from soundraw_music_generator.skill import get_skill_info

info = get_skill_info()
print(info["capabilities"])
print(info["input_schema"])
```

### Execute as Skill

```python
output = generator.execute_skill({
    "genre": "orchestral",
    "mood": "epic",
    "duration": 90,
    "tempo": 120,
    "energy": 8
})

if output["status"] == "success":
    print(f"Generated: {output['data']['file_path']}")
else:
    print(f"Error: {output['error']}")
```

---

## Error Handling

### Common Errors

#### Invalid API Key
```
Error: Invalid API key
```
**Solution**:
1. Check: `echo $SOUNDRAW_API_KEY`
2. Verify format from Soundraw dashboard
3. Generate new key if needed

#### Unknown Genre
```
Error: Unknown genre 'xyz'
```
**Solution**:
Use `SoundrawMusicGenerator.list_genres()` to see valid genres

#### Unknown Mood
```
Error: Unknown mood 'xyz'
```
**Solution**:
Use `SoundrawMusicGenerator.list_moods()` to see valid moods (40+ available)

#### Generation Timeout
```
Error: Generation did not complete within 180 seconds
```
**Solution**:
1. Try with shorter duration
2. Increase `max_wait_time`: `max_wait_time=300`
3. Simplify instrumentation description
4. Try again

#### Quota Exceeded
```
Error: Monthly generation quota exceeded
```
**Solution**:
1. Upgrade subscription plan
2. Wait for next billing cycle
3. Check usage in Soundraw dashboard

---

## Troubleshooting

### Generation Too Slow

**Soundtrack generations take longer than other providers**:
- Typical time: 30-120 seconds
- Complex compositions: longer
- Increase `max_wait_time` if timing out

### File Not Saving

**Check permissions**:
```bash
mkdir -p $MUSIC_OUTPUT_DIR
chmod 755 $MUSIC_OUTPUT_DIR
ls -la $MUSIC_OUTPUT_DIR
```

### Wrong Audio Quality

- **Too quiet**: Increase `energy` (8-10)
- **Too loud**: Decrease `energy` (1-3)
- **Wrong instrument**: Try different `instrumentation`
- **Wrong mood**: Try different genre/mood combination

### Best Practices for Quality

```python
# Professional video score
result = generator.generate_music(
    genre="cinematic",
    mood="dramatic",
    duration=120,
    tempo=90,
    energy=7,
    instrumentation="full orchestra with dramatic strings"
)

# High quality ambient
result = generator.generate_music(
    genre="ambient",
    mood="ethereal",
    duration=300,
    tempo=70,
    energy=2,
    instrumentation="pads and atmospheric effects"
)
```

---

## Best Practices

### For Commercial Use

✅ **Do**:
- Check subscription includes commercial license
- Use for YouTube, TikTok, streaming
- Use in video, podcasts, ads
- Modify or customize as needed

❌ **Don't**:
- Resell the tracks as-is
- Use on other music platforms
- Sell access to generated tracks
- Claim ownership of composition

### Quality Tips

- Use **specific instrumentation** descriptions for tailored results
- Specify **tempo** to match your content pacing
- Use **higher energy** for prominent roles, **lower** for background
- Experiment with different **mood/genre** combinations
- Try **longer durations** for complex compositions

---

## Security

- ✅ API keys stored in environment variables only
- ✅ HTTPS/TLS encryption on all communications
- ✅ No credentials hardcoded in source code
- ✅ No sensitive data in version control
- ✅ Local files saved with restricted permissions (0600)

### Token Management

```bash
# GOOD: Environment variable
export SOUNDRAW_API_KEY="..."
python script.py

# BAD: Hardcoding
api_key = "..."  # Never do this!

# ALSO BAD: Git commit
git add config.py  # If contains API key
```

---

## Version History

### v1.0.0 - Initial Release (2026-02-15)
- ✨ Full Soundraw API integration
- 🎼 Support for 20+ genres and 40+ moods
- 🎻 Instrumentation control
- 🎵 Tempo and energy specification
- 📥 Auto-download to local directory
- 🔒 Secure API key handling
- ✅ Production-ready

---

## Support

- **Soundraw Website**: https://www.soundraw.io
- **API Documentation**: https://www.soundraw.io/api
- **Support Email**: support@soundraw.io
- **Community**: Forum at soundraw.io

---

## License

Part of OpenClaw Skills Platform. See main LICENSE.

Generated music is royalty-free with commercial license included for all subscription tiers.
