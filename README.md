# OpenClaw Music Generation Skills

Complete suite of skills for generating music using AI. This workspace contains three integrated skills that work together to convert themes into downloadable music files.

## 📦 Skills Overview

### 1. **ChatGPT Prompt Generator** 
- Converts a theme into a detailed music creation prompt
- Uses OpenAI's ChatGPT API
- Output: Structured music generation prompt
- Location: `skills/chatgpt-prompt-generator/`

### 2. **Suno AI Music Generator**
- Generates music files from detailed prompts
- Uses Suno AI API with async polling
- Output: Download URL to generated music file
- Location: `skills/suno-music-generator/`

### 3. **Music Generation Orchestrator** ⭐ **START HERE**
- End-to-end skill that chains together Skills 1 & 2
- Single input: theme/topic
- Output: Direct download link to music file
- Location: `skills/music-orchestrator/`
- **Easiest to use - recommended for most use cases**

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd "u:/OneDrive - Suptecon GmbH/Dokumente/openclaw skills/clawskills"
```

### 2. Install Shared Dependencies

```bash
pip install python-dotenv requests openai
```

### 3. Create `.env` File

```bash
# Create a .env file in the workspace root
cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4
OPENAI_TIMEOUT=30

# Suno AI Configuration
SUNO_API_KEY=your-suno-api-key-here
SUNO_API_BASE_URL=https://api.suno.ai
SUNO_TIMEOUT=60
SUNO_MAX_RETRIES=30
SUNO_RETRY_DELAY=2
EOF
```

### 4. Test the Orchestrator

```python
import sys
sys.path.insert(0, 'skills')

from music_orchestrator.skill import execute_skill

result = execute_skill({
    "theme": "tropical beach sunset"
})

if result['status'] == 'success':
    print(f"✅ Music generated!")
    print(f"📥 Download: {result['download_url']}")
    print(f"🎵 Song ID: {result['song_id']}")
else:
    print(f"❌ Error: {result['message']}")
```

## 📁 Directory Structure

```
clawskills/
├── .workspace-rules.md                 # Workspace rules and guidelines
├── shared/                             # Shared utilities
│   ├── __init__.py
│   └── utils.py                       # Common functions (validation, security, logging)
│
├── skills/
│   ├── chatgpt-prompt-generator/      # Skill 1: Theme → Prompt
│   │   ├── skill.py                   # Main implementation
│   │   ├── config.yaml                # Configuration
│   │   ├── requirements.txt           # Dependencies
│   │   └── SKILL.md                   # Detailed documentation
│   │
│   ├── suno-music-generator/          # Skill 2: Prompt → Music
│   │   ├── skill.py                   # Main implementation
│   │   ├── config.yaml                # Configuration
│   │   ├── requirements.txt           # Dependencies
│   │   └── SKILL.md                   # Detailed documentation
│   │
│   └── music-orchestrator/            # Skill 3: Theme → Music (Complete Pipeline)
│       ├── skill.py                   # Main implementation
│       ├── config.yaml                # Configuration
│       ├── requirements.txt           # Dependencies
│       └── SKILL.md                   # Detailed documentation
│
└── docs/                              # Additional documentation
    └── ARCHITECTURE.md                # Technical architecture details
```

## 🔐 Security

All skills follow security-first principles:

✅ **API Keys**: Stored in environment variables, never logged  
✅ **Input Validation**: All user inputs validated for length and format  
✅ **Error Handling**: Safe error messages without exposing internals  
✅ **No Sensitive Logging**: API keys and tokens never appear in logs  
✅ **HTTPS Only**: All external API calls use HTTPS  
✅ **Timeout Protection**: Prevents hanging requests  

## 🛠️ Skills Comparison

| Feature | Skill 1 | Skill 2 | Skill 3 |
|---------|---------|---------|---------|
| Takes theme input | ❌ | ❌ | ✅ |
| Takes prompt input | ❌ | ✅ | ❌ |
| Uses ChatGPT | ✅ | ❌ | ✅ |
| Uses Suno AI | ❌ | ✅ | ✅ |
| Returns prompt | ✅ | ❌ | ✓ (in workflow) |
| Returns music URL | ❌ | ✅ | ✅ |
| **Ease of Use** | Intermediate | Intermediate | **Easy** ⭐ |

## 📚 Detailed Documentation

### For Individual Skills

- [ChatGPT Prompt Generator](skills/chatgpt-prompt-generator/SKILL.md)
- [Suno AI Music Generator](skills/suno-music-generator/SKILL.md)
- [Music Generation Orchestrator](skills/music-orchestrator/SKILL.md)

### For Developers

- [Architecture & Design](docs/ARCHITECTURE.md) (coming soon)
- [API Integration Guide](docs/API_INTEGRATION.md) (coming soon)
- [Security Guidelines](docs/SECURITY.md) (coming soon)

## 🌟 Usage Scenarios

### Scenario 1: Simple Music Generation (Recommended)

Just want music from a theme? Use the **Orchestrator**:

```python
from skills.music_orchestrator.skill import execute_skill

result = execute_skill({"theme": "cyberpunk city"})
# Returns: Download link to music!
```

### Scenario 2: Custom Prompt Generation

Need a specific music prompt?

```python
from skills.chatgpt_prompt_generator.skill import ChatGPTPromptGenerator

generator = ChatGPTPromptGenerator()
result = generator.generate_prompt("ambient electronic")
# Returns: Custom prompt for Suno
```

### Scenario 3: Generate from Existing Prompt

Have your own prompt? Generate music directly:

```python
from skills.suno_music_generator.skill import SunoAIMusicGenerator

generator = SunoAIMusicGenerator()
result = generator.generate_music("Your custom music prompt here...")
# Returns: Download link to music
```

## 🔄 Workflow Pipeline

```
Theme
  ↓
[ChatGPT] → Generates Prompt
  ↓
[Suno AI] → Generates Music
  ↓
Download Link
```

## ⚡ Performance

| Step | Time | API Calls |
|------|------|-----------|
| Prompt Generation | ~3-5s | 1 |
| Music Generation | ~60s | 15-30 (polling) |
| **Total** | **~90s** | **16-31** |

## 🆘 Troubleshooting

### "API Key Not Found"
```bash
# Ensure environment variables are set
export OPENAI_API_KEY="your-key"
export SUNO_API_KEY="your-key"

# Or use .env file
source .env
```

### "Rate Limit Exceeded"
- Wait a few minutes
- Check API quotas at:
  - https://platform.openai.com/account/billing/overview (OpenAI)
  - https://www.suno.ai/ (Suno)

### "Music Generation Timeout"
- Suno API is slow
- Solution: Increase `SUNO_MAX_RETRIES` in .env
- Or try again later when Suno is less busy

### "Invalid Theme"
- Theme contains invalid characters
- Keep to: letters, numbers, spaces, hyphens, commas
- Example: `"cyberpunk city at night"` ✅
- Example: `"cyberpunk<script>"` ❌

## 📝 Configuration Files

Each skill has a `config.yaml`:

- **chatgpt-prompt-generator/config.yaml**: ChatGPT settings, input constraints
- **suno-music-generator/config.yaml**: Suno API settings, polling config
- **music-orchestrator/config.yaml**: Workflow definition, dependencies

Edit these to customize behavior.

## 🧪 Testing

### Unit Test Individual Skills

```bash
# Test ChatGPT skill
python skills/chatgpt-prompt-generator/skill.py

# Test Suno skill
python skills/suno-music-generator/skill.py

# Test Orchestrator
python skills/music-orchestrator/skill.py
```

### Integration Test

```python
import sys
sys.path.insert(0, 'skills')

from music_orchestrator.skill import execute_skill

# Full orchestration test
result = execute_skill({
    "theme": "rainy evening coffee shop",
    "tags": "lo-fi,chill,ambient"
})

print(f"Status: {result['status']}")
print(f"Theme: {result['theme']}")
print(f"Download: {result['download_url']}")
print(f"Song ID: {result['song_id']}")
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- pip (Python package manager)
- Internet connection (OpenAI & Suno APIs)

### API Requirements
- Valid OpenAI API key (GPT-4 or higher model)
- Valid Suno AI API key
- Sufficient API credits with both providers

### Storage
- Minimal disk space (code only ~50KB)
- Download music files as needed into your storage

## 🎯 Success Criteria

✅ **Simple**: Just pass a theme, get music back  
✅ **Fast**: Complete in ~90 seconds  
✅ **Reliable**: Handles errors gracefully  
✅ **Secure**: All keys and data protected  
✅ **Transparent**: Complete workflow reporting  

## 🚀 Next Steps

1. **Setup**: Install dependencies and configure API keys
2. **Test**: Run quick test with the Orchestrator
3. **Integrate**: Import skills into your OpenClaw application
4. **Monitor**: Watch logs for any issues
5. **Scale**: Adjust timeouts and retries as needed

## 📞 Support

### Documentation
- Detailed READMEs in each skill folder
- Configuration files with explanations
- Error messages are descriptive

### Debugging
- Check `.env` file for API keys
- Review logs in terminal output
- Test individual steps manually
- Verify API keys have sufficient quota

### API Status
- OpenAI Status: https://status.openai.com/
- Suno Status: https://www.suno.ai/

## 📄 License

These skills are part of the OpenClaw platform.

---

**Ready to create music?** Start with the [Music Generation Orchestrator](skills/music-orchestrator/SKILL.md)!
