# Music Generation Skills - Architecture & Design

## Overview

The OpenClaw Music Generation Skills suite consists of three modular skills that work together to convert themes into downloadable music files. The architecture follows security-first and zero-trust principles.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw Platform                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                ┌─────────────────────────────┐
                │  Music Orchestrator (Skill) │
                │   (Entry Point)             │
                └────────────┬────────────────┘
                             │
                 ┌───────────┴───────────┐
                 ↓                       ↓
        ┌─────────────────────┐  ┌──────────────────────┐
        │ ChatGPT Prompt Gen  │  │ Suno AI Music Gen    │
        │ (Skill 1)           │  │ (Skill 2)            │
        └────────┬────────────┘  └─────────┬────────────┘
                 ↓                          ↓
        ┌─────────────────────┐  ┌──────────────────────┐
        │  OpenAI API         │  │  Suno AI API         │
        │  (ChatGPT)          │  │  (with polling)      │
        └─────────────────────┘  └──────────────────────┘
                 ↓                          ↓
        ┌─────────────────────┐  ┌──────────────────────┐
        │  Generated Prompt   │  │  Music File URL      │
        └─────────────────────┘  └──────────────────────┘
```

## Core Components

### 1. Shared Utilities (`shared/utils.py`)

**Purpose**: Common functions and security wrappers

**Key Classes/Functions**:
- `SecurityError`: Exception for security violations
- `ValidationError`: Exception for validation failures
- `get_secure_api_key()`: Safely retrieve API keys from environment
- `validate_string_input()`: Validate user input with constraints
- `validate_theme()`: Theme-specific validation
- `safe_log_api_call()`: Log API calls without exposing secrets

**Security Features**:
- ✅ API keys never logged
- ✅ Input validation with regex patterns
- ✅ Error messages safe for users
- ✅ Sensitive data redaction

### 2. ChatGPT Prompt Generator (`skills/chatgpt-prompt-generator/skill.py`)

**Purpose**: Convert user themes into detailed music prompts

**Class**: `ChatGPTPromptGenerator`

**Key Methods**:
```python
generate_prompt(theme: str) -> Dict[str, Any]
```

**Workflow**:
1. Validate theme input (3-500 characters)
2. Send to ChatGPT with system prompt
3. Return structured prompt
4. Handle errors (rate limits, auth, timeout)

**Security**:
- ✅ API key in environment only
- ✅ Input validation (length, characters)
- ✅ Error handling without exposing internals
- ✅ Safe logging

**Error Handling**:
- Rate limit: Graceful retry message
- Authentication: Clear auth error
- API error: Generic message with logging
- Timeout: Timeout-specific message

### 3. Suno AI Music Generator (`skills/suno-music-generator/skill.py`)

**Purpose**: Generate music files from detailed prompts

**Class**: `SunoAIMusicGenerator`

**Key Methods**:
```python
generate_music(prompt: str, tags: Optional[str]) -> Dict[str, Any]
```

**Workflow**:
1. Validate prompt (10-2000 characters)
2. Send POST to Suno API to initiate generation
3. Receive song_id from response
4. Poll for completion (up to 30 retries with 2s delay)
5. Return download URL and metadata
6. Handle timeouts and errors

**Polling Strategy**:
```
Send Request → Get song_id
     ↓
Poll Status (GET /v1/songs/{id})
     ↓
Loop until complete or timeout:
  - Check status field
  - If "complete" → return audio_url
  - If "error" → return error
  - If "generating" → wait 2s, retry (max 30 times)
```

**Security**:
- ✅ API key in environment only
- ✅ HTTPS for all requests
- ✅ Timeout protection (prevents hanging)
- ✅ Error handling without exposing API details
- ✅ Input validation

**Error Handling**:
- API error: Status code in response
- Generation timeout: After 30 retries (~60 seconds)
- Network error: Connection issues handled
- Invalid response: No song_id check

### 4. Music Generation Orchestrator (`skills/music-orchestrator/skill.py`)

**Purpose**: End-to-end workflow automation

**Class**: `MusicGenerationOrchestrator`

**Key Methods**:
```python
generate_music_from_theme(theme: str, tags: Optional[str]) -> Dict[str, Any]
```

**Workflow**:
```
Step 1: Validate Input
   ↓
Step 2: Initialize Services
   - ChatGPTPromptGenerator()
   - SunoAIMusicGenerator()
   ↓
Step 3: Generate Prompt
   - Call skill 1 with theme
   - Check for success
   ↓
Step 4: Generate Music
   - Call skill 2 with generated prompt
   - Check for success
   ↓
Step 5: Return Result
   - Include download URL
   - Include complete workflow details
   - Include metadata
```

**Error Handling**:
- Early exit on validation failure
- Step 1 failure → return error with context
- Step 2 failure → return error with generated prompt
- All errors include workflow context for debugging

## Data Flow

### Request Flow

```
User Input (theme)
     ↓
Validation (length, characters)
     ↓
ChatGPT Prompt Generation
     ├─ OpenAI API call
     ├─ Error handling (rate limit, auth, timeout)
     └─ Output: music prompt
     ↓
Suno Music Generation
     ├─ Initiate generation (POST)
     ├─ Get song_id
     ├─ Poll for completion (GET with retry)
     ├─ Error handling (timeout, API error, generation error)
     └─ Output: music file URL
     ↓
Return Complete Result
     ├─ Status (success/error)
     ├─ Download URL
     ├─ Song metadata
     ├─ Workflow details
     └─ Timestamp
```

### Response Structure

```json
{
  "status": "success|error",
  "theme": "input theme",
  "download_url": "https://...", // on success
  "song_id": "unique_id",
  "error_type": "...",           // on error
  "message": "...",              // on error
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
  },
  "timestamp": "2026-02-15T..."
}
```

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────┐
│  Layer 1: Input Validation              │
│  - Length checks                         │
│  - Character validation (regex)          │
│  - Type checking                         │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Layer 2: Authentication                │
│  - API keys from environment only        │
│  - No hardcoded secrets                  │
│  - Key validation                        │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Layer 3: API Communication             │
│  - HTTPS only                            │
│  - Timeout protection                    │
│  - Error handling                        │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Layer 4: Data Protection               │
│  - No sensitive logging                  │
│  - Error messages are safe               │
│  - No data persistence                   │
└─────────────────────────────────────────┘
```

### API Key Management

**Never Stored**:
- ❌ In source code
- ❌ In configuration files
- ❌ In logs
- ❌ In error messages

**Always Stored**:
- ✅ Environment variables
- ✅ `.env` file (local only, gitignored)
- ✅ Secure secret management (in production)

**Access Pattern**:
```python
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise SecurityError("API key not found")
# Use api_key (never log it!)
```

### Error Messages Safe Pattern

```python
# ❌ UNSAFE: Exposes internal details
"OpenAI API error: Invalid API key format: sk-proj..."

# ✅ SAFE: Generic, safe for users
"Failed to authenticate with OpenAI API."
```

## Extension Points

### Adding a New Music Service

Instead of Suno, support another music AI:

1. Create `skills/new-service-generator/`
2. Implement `execute_skill(parameters)` function
3. Follow error structure
4. Update Orchestrator to include new service
5. Add integration tests

### Modifying Prompt Generation

Change how ChatGPT creates prompts:

1. Edit `ChatGPTPromptGenerator.SYSTEM_PROMPT`
2. Adjust example prompts
3. Modify `generate_prompt()` logic
4. Test with various themes

### Customizing Parameters

Add new configuration in `.env`:

1. Add to `.env.template`
2. Read with `os.getenv()`
3. Document in config.yaml
4. Add validation if needed

## Performance Optimization

### Current Bottlenecks

1. **Suno Generation Time**: ~60 seconds (no control)
2. **Polling Overhead**: ~20-30 API calls (configurable via `SUNO_MAX_RETRIES`)
3. **ChatGPT Response**: 3-5 seconds (depends on OpenAI load)

### Optimization Strategies

**1. Reduce Polling Calls**:
- Increase `SUNO_RETRY_DELAY` (2s → 5s)
- Reduce `SUNO_MAX_RETRIES` if faster failure acceptable
- Risk: Might miss completion, timeout instead

**2. Parallel Processing** (Future):
- Currently sequential (Prompt → Music)
- Could generate multiple prompts in parallel
- Could queue music generations

**3. Caching** (Future):
- Cache themes that have been seen before
- Cache generated prompts
- Risk: Quality vs speed tradeoff

**4. Shorter Timeouts** (Future):
- Use more aggressive polling
- Trade API calls for faster feedback

## Testing Strategy

### Unit Tests

Test individual skills:
```python
# Test ChatGPT skill
def test_chatgpt_valid_theme():
    generator = ChatGPTPromptGenerator()
    result = generator.generate_prompt("test theme")
    assert result['status'] == 'success'

# Test Suno skill
def test_suno_invalid_prompt():
    generator = SunoAIMusicGenerator()
    result = generator.generate_music("short")
    assert result['status'] == 'error'
```

### Integration Tests

Test orchestrator:
```python
def test_orchestrator_complete_flow():
    result = execute_skill({"theme": "test"})
    assert result['status'] in ['success', 'error']
    assert all(k in result for k in ['timestamp', 'workflow'])
```

### Error Path Tests

Test failure scenarios:
```python
# No API key
# Invalid theme
# API timeouts
# Generation failures
```

## Monitoring & Logging

### What Gets Logged

✅ **Safe to Log**:
- Timestamp
- Operation name
- Success/failure status
- Input length (not content)
- Error types
- Response times

❌ **Never Log**:
- API keys
- Full prompts (sensitive content)
- User input (privacy)
- API responses (may contain sensitive data)
- Full error details from external APIs

### Log Format

```
2026-02-15T10:30:45.123Z - music_orchestrator - INFO - API: OpenAI/ChatGPT | Operation: generate_music_prompt | Status: success | Details: {'theme_length': 25, 'model': 'gpt-4'}
```

## Deployment Considerations

### Environment Variables Required

```bash
# Production setup
export OPENAI_API_KEY="prod-key"
export SUNO_API_KEY="prod-key"
export OPENAI_MODEL="gpt-4"
export LOG_LEVEL="WARNING"  # Not DEBUG in production
```

### Rate Limiting Recommendations

**For OpenAI**:
- Default limits usually sufficient
- Monitor usage at https://platform.openai.com/usage
- Consider rate limiting at application level

**For Suno**:
- Check API quota
- Stagger requests if many concurrent users
- Implement queue system if needed

### Scalability

**Horizontal Scaling**:
- Skills are stateless (can run anywhere)
- Add more instances behind load balancer
- Monitor API rate limits

**Vertical Scaling**:
- Increase timeouts for slower machines
- Reduce polling frequency
- Cache prompts for repeated themes

## Future Enhancements

### Planned Features

1. **Multiple Music Services**: Support multiple AI music generators
2. **Caching Layer**: Cache generated prompts and music
3. **Quality Settings**: Allow users to control generation quality
4. **Style Templates**: Pre-made prompt templates for different genres
5. **Batch Processing**: Generate multiple songs at once
6. **WebUI**: Web interface for easier use

### Architecture Changes

1. **Database**: Store generated prompts and music metadata
2. **Queue System**: Handle high volume of simultaneous requests
3. **CDN Integration**: Faster music file delivery
4. **Microservices**: Separate services for each skill
5. **GraphQL API**: More flexible querying

---

**Questions?** See the individual skill READMEs or workspace documentation.
