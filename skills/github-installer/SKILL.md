# GitHub Installer Skill

## Overview

This skill enables OpenClaw to automatically pull code, skills, files, and tools from GitHub repositories. It includes built-in support for:

- **GitHub Authentication** - Secure token-based access to public and private repositories
- **OpenClaw Skill Auto-Detection** - Automatically detects and installs OpenClaw skills
- **Google OAuth Integration** - Optional OAuth 2.0 authentication flow
- **Backup & Restore** - Safely update existing skills with backups
- **Shallow Cloning** - Fast downloads with minimal bandwidth

## Features

✅ **GitHub Repository Cloning** - Clone or update repositories with a single call  
✅ **Token-Based Authentication** - Secure GitHub API access  
✅ **Auto-Detect OpenClaw Skills** - Finds skills using standard markers (config.yaml, skill.py, SKILL.md)  
✅ **Automatic Installation** - Copies detected skills to target directory  
✅ **Backup Management** - Creates backups before replacing existing skills  
✅ **Google OAuth Support** - Optional OAuth 2.0 for additional authentication flows  
✅ **Path Validation** - Prevents directory traversal attacks  
✅ **Shallow Cloning** - Uses `--depth 1` for fast downloads  
✅ **Security-First Design** - API keys stored in environment, never logged  

## Usage

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repository_url` | string | Yes | GitHub repo URL (https://github.com/owner/repo, owner/repo, or git@github.com:owner/repo) |
| `branch` | string | No | Git branch to clone (default: main) |
| `action` | string | No | What to do: clone, install_skills, or clone_and_install (default: clone_and_install) |
| `target_dir` | string | No | Installation directory (default: ./skills/) |
| `google_auth_required` | boolean | No | Enable Google OAuth (default: false) |

### Output

```json
{
  "status": "success|partial|error|warning",
  "repository": "https://github.com/owner/repo",
  "branch": "main",
  "clone_status": "cloned|updated",
  "repository_path": "/path/to/cloned/repo",
  "installation": {
    "status": "success|partial",
    "skills_detected": 3,
    "skills_installed": [
      {
        "name": "skill-name",
        "path": "/path/to/skill",
        "status": "installed"
      }
    ],
    "skills_failed": [],
    "target_directory": "/path/to/skills"
  },
  "google_oauth": {
    "oauth_available": true,
    "authorization_url": "https://accounts.google.com/o/oauth2/...",
    "state": "..."
  },
  "timestamp": "2026-02-15T..."
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required: GitHub Token
export GITHUB_TOKEN="ghp_your_github_personal_access_token"

# Optional: GitHub API configuration
export GITHUB_API_BASE_URL="https://api.github.com"
export GITHUB_TIMEOUT="30"
export BACKUP_ENABLED="true"

# Optional: Google OAuth (for optional authentication flows)
export GOOGLE_OAUTH_CLIENT_ID="your-google-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-google-client-secret"
export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8080/callback"
```

### 3. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" (classic)
3. Select scopes:
   - `repo` (full control of private repositories)
   - `read:user` (read user profile data)
4. Generate the token
5. Copy to `.env` file: `GITHUB_TOKEN=ghp_...`

## Usage Examples

### Example 1: Clone Repository

```python
from skills.github_installer.skill import execute_skill

result = execute_skill({
    "repository_url": "https://github.com/Cenralsolution/clawskills",
    "branch": "main",
    "action": "clone"
})

print(f"Status: {result['status']}")
print(f"Cloned to: {result['repository_path']}")
```

### Example 2: Clone and Auto-Install Skills

```python
from skills.github_installer.skill import execute_skill

result = execute_skill({
    "repository_url": "Cenralsolution/clawskills",  # Shorthand format
    "action": "clone_and_install"
})

if result['status'] == 'success':
    print(f"Installed {len(result['installation']['skills_installed'])} skills")
    for skill in result['installation']['skills_installed']:
        print(f"  ✓ {skill['name']}")
```

### Example 3: Update Existing Repository

```python
from skills.github_installer.skill import execute_skill

result = execute_skill({
    "repository_url": "owner/repo",
    "branch": "develop",
    "target_dir": "./my-cloned-repo"
})

# If repo already exists, it performs git pull instead
print(f"Action: {result['clone_status']}")  # "cloned" or "updated"
```

### Example 4: With Google OAuth

```python
from skills.github_installer.skill import execute_skill

result = execute_skill({
    "repository_url": "owner/repo",
    "google_auth_required": True
})

if result['google_oauth']['oauth_available']:
    auth_url = result['google_oauth']['authorization_url']
    state = result['google_oauth']['state']
    
    # Redirect user to auth_url
    print(f"Please authorize at: {auth_url}")
    
    # Save state for later verification
    save_oauth_state(state)
```

### Example 5: Batch Installation

```python
from skills.github_installer.skill import execute_skill

repositories = [
    "owner/repo1",
    "owner/repo2",
    "owner/repo3"
]

for repo in repositories:
    result = execute_skill({
        "repository_url": repo,
        "action": "clone_and_install"
    })
    
    if result['status'] in ['success', 'partial']:
        print(f"✓ {repo}: {len(result['installation']['skills_installed'])} skills installed")
    else:
        print(f"✗ {repo}: {result['message']}")
```

## Security

### API Key Management

🔒 **GitHub Token Storage**
- Stored ONLY in environment variables
- Never logged or exposed in responses
- Use GitHub personal access tokens (not passwords)
- Regenerate tokens periodically
- Limit token scopes to minimum required

🔒 **Path Security**
- All file paths validated to prevent directory traversal
- Only relative paths allowed
- Cannot use `../` sequences
- Validates against base directory

🔒 **Google OAuth Security**
- OAuth 2.0 authorization flow (not implicit)
- CSRF protection with state tokens
- Secure redirect URI validation
- Scopes are minimal and configurable

### Authentication Types

#### GitHub Token (Required)

```bash
# Create at https://github.com/settings/tokens
export GITHUB_TOKEN="ghp_..."

# For private repositories, token must have 'repo' scope
# For public repositories, can use 'public_repo' scope only
```

#### Google OAuth (Optional)

Provides optional OAuth 2.0 authentication flow for scenarios where Google authorization is needed:

```python
# Get OAuth authorization URL
result = execute_skill({
    "repository_url": "owner/repo",
    "google_auth_required": True
})

# Redirect user to authorization URL
redirect_to(result['google_oauth']['authorization_url'])

# User grants permissions
# Your app receives authorization code
# Exchange code for access token (implement on your backend)
```

## Error Handling

The skill handles the following scenarios:

### Clone Errors
- **Repository not found** - Repository URL is invalid or repository doesn't exist
- **Authentication failed** - GitHub token is invalid or lacks permissions
- **Timeout** - Git operation took too long
- **Network error** - Connection issues

### Installation Errors
- **Path traversal detected** - Malicious path attempted
- **Directory already exists** - Target directory exists (backed up if enabled)
- **Permission denied** - Cannot write to target directory
- **Invalid structure** - Files cannot be copied

### Validation Errors
- **Invalid repository URL** - URL format is incorrect
- **Invalid branch name** - Branch contains invalid characters
- **Invalid target path** - Path attempts escape base directory

## Error Recovery

### Backup and Restore

If `BACKUP_ENABLED=true`:

```bash
# Before replacing an existing skill:
skills/skill-name/           # Original
skills/skill-name.backup.2026-02-15T.../ # Backup created

# To restore:
rm -rf skills/skill-name
mv skills/skill-name.backup.2026-02-15T.../ skills/skill-name
```

### Common Issues

#### Issue: "GitHub token not found"
```bash
# Solution: Ensure GITHUB_TOKEN is set
export GITHUB_TOKEN="ghp_..."
```

#### Issue: "Repository not found" (but repository exists)
```bash
# Solution: Verify token has 'repo' scope
# Go to https://github.com/settings/tokens and check scopes
```

#### Issue: "Permission denied" when installing skills
```bash
# Solution: Ensure target directory is writable
chmod 755 ./skills/
```

#### Issue: "Git timeout"
```bash
# Solution: Increase timeout
export GITHUB_TIMEOUT="60"
```

## Auto-Detection of OpenClaw Skills

The skill automatically detects OpenClaw repositories by looking for standard markers:

```
repository/
├── skills/
│   └── my-skill/
│       ├── config.yaml         ✓ Marker
│       ├── skill.py            ✓ Marker
│       ├── SKILL.md            ✓ Marker
│       └── requirements.txt
└── docs/
```

### Detection Process

1. Recursively scans all directories in repository
2. Looks for all three markers (config.yaml, skill.py, SKILL.md)
3. Collects full path and details for each skill
4. Copies detected skills to target directory

### Custom Installation

If you want to install only specific files:

```python
# Use "clone" action only, then manually select files
result = execute_skill({
    "repository_url": "owner/repo",
    "action": "clone"
})

# Manually copy what you need from result['repository_path']
```

## Integration with OpenClaw

This skill integrates with OpenClaw's framework:

```python
from skills.github_installer.skill import execute_skill

# Standard OpenClaw interface
result = execute_skill(parameters_dict)
```

Can be used to:
1. Download and install community skills
2. Update internal tools
3. Pull configuration files
4. Manage multi-repository deployments

## Advanced Usage

### Shallow Cloning

The skill uses shallow cloning (`--depth 1`) by default:

```bash
# Benefits:
# - Faster downloads (only latest commit)
# - Smaller disk usage
# - No full history

# If you need full history, customize the skill code
```

### GitHub Linking

```python
# Get OAuth URL for user authentication
result = execute_skill({
    "repository_url": "owner/repo",
    "google_auth_required": True
})

if result['google_oauth']['oauth_available']:
    # Implement OAuth flow to link Google account
    # Then use linked account for additional automations
```

## Troubleshooting

### Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Then run skill
result = execute_skill({...})
```

### Verify Git Installation

```bash
git --version
# Should output: git version 2.xx.x
```

### Verify GitHub Access

```bash
git clone https://$GITHUB_TOKEN@github.com/owner/repo.git
# Should work without prompting for password
```

### Check Rate Limits

```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

## Limitations

⚠️ **Shallow Cloning** - Full history not available (use custom implementation if needed)

⚠️ **Git Required** - Skill requires Git CLI to be installed and in PATH

⚠️ **GitHub API Rate Limits** - Unauthenticated: 60 requests/hour, Authenticated: 5000 requests/hour

⚠️ **File Size** - May be slow with very large repositories (>1GB)

⚠️ **Large File Storage (LFS)** - Git LFS not automatically supported (use custom implementation if needed)

## Support

For issues or questions:
1. Verify GitHub token is valid and has proper scopes
2. Check that Git is installed: `git --version`
3. Check GitHub status: https://www.githubstatus.com/
4. Review error messages and logs
5. Test with a small public repository first
6. Verify network connectivity

---

**Next Steps:** After cloning repositories, combine with other OpenClaw skills to automate your workflow!
