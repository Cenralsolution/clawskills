"""
GitHub Installer Skill for OpenClaw
Pulls code, skills, files, and tools from GitHub repositories with authentication support
"""

import logging
import json
import os
import shutil
import subprocess
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import (
    ValidationError,
    SecurityError,
    get_secure_api_key,
    validate_repository_url,
    validate_branch_name,
    validate_file_path,
    GoogleOAuthConfig,
    validate_oauth_code,
    safe_log_api_call,
    get_timestamp
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class GitHubInstaller:
    """
    GitHub Installer Skill for OpenClaw
    
    Handles:
    - GitHub repository cloning and pulling
    - Token-based authentication
    - Google OAuth integration (optional)
    - Auto-detection of OpenClaw skills
    - File and tool installation
    - Backup and restoration
    """
    
    OPENCLAW_SKILL_MARKERS = ['config.yaml', 'skill.py', 'SKILL.md']
    
    def __init__(self):
        """Initialize GitHub Installer"""
        try:
            self.github_token = get_secure_api_key('GITHUB_TOKEN')
            self.github_api_base = os.getenv('GITHUB_API_BASE_URL', 'https://api.github.com')
            self.timeout = int(os.getenv('GITHUB_TIMEOUT', '30'))
            self.backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
            self.google_oauth = GoogleOAuthConfig()
            logger.info("GitHub Installer initialized successfully")
        except SecurityError as e:
            logger.error(f"Failed to initialize GitHub Installer: {e}")
            raise
    
    def clone_repository(self, repo_url: str, branch: str = 'main', 
                        target_dir: str = None) -> Dict[str, Any]:
        """
        Clone or update a GitHub repository.
        
        Args:
            repo_url: Repository URL (https://github.com/owner/repo or owner/repo)
            branch: Branch to checkout
            target_dir: Directory to clone into (optional)
            
        Returns:
            Dictionary with clone status and details
        """
        try:
            # Validate inputs
            validated_url = validate_repository_url(repo_url)
            validated_branch = validate_branch_name(branch)
            
            logger.info(f"Cloning repository: {validated_url} (branch: {validated_branch})")
            
            safe_log_api_call(
                "GitHub",
                "clone_repository",
                "starting",
                {"repository": validated_url, "branch": validated_branch}
            )
            
            # Determine target directory
            if target_dir is None:
                repo_name = validated_url.split('/')[-1].replace('.git', '')
                target_dir = os.path.join(os.getcwd(), repo_name)
            
            target_dir = validate_file_path(target_dir)
            
            # Check if directory exists (for git pull)
            if os.path.exists(os.path.join(target_dir, '.git')):
                logger.info(f"Repository exists at {target_dir}, pulling latest changes...")
                result = self._git_pull(target_dir, validated_branch)
            else:
                # Create parent directory if needed
                os.makedirs(os.path.dirname(os.path.abspath(target_dir)), exist_ok=True)
                result = self._git_clone(validated_url, target_dir, validated_branch)
            
            safe_log_api_call(
                "GitHub",
                "clone_repository",
                "success",
                {"repository": validated_url, "target_dir": target_dir}
            )
            
            return result
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            safe_log_api_call("GitHub", "clone_repository", "error", 
                            {"error_type": type(e).__name__})
            return {
                "status": "error",
                "error_type": "clone_failed",
                "message": str(e),
                "timestamp": get_timestamp()
            }
    
    def _git_clone(self, repo_url: str, target_dir: str, branch: str) -> Dict[str, Any]:
        """Execute git clone command"""
        try:
            cmd = [
                'git', 'clone',
                '--branch', branch,
                '--depth', '1',  # Shallow clone for speed
                '--'
            ]
            
            # Use GitHub token for authentication
            if self.github_token:
                authenticated_url = repo_url.replace(
                    'https://github.com/',
                    f'https://{self.github_token}@github.com/'
                )
                cmd.append(authenticated_url)
            else:
                cmd.append(repo_url)
            
            cmd.append(target_dir)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return {
                    "status": "error",
                    "error_type": "git_clone_failed",
                    "message": result.stderr,
                    "timestamp": get_timestamp()
                }
            
            logger.info(f"Repository cloned successfully to {target_dir}")
            
            return {
                "status": "success",
                "action": "cloned",
                "repository": repo_url,
                "branch": branch,
                "target_dir": target_dir,
                "timestamp": get_timestamp()
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Git clone timed out")
            return {
                "status": "error",
                "error_type": "timeout",
                "message": "Git clone operation timed out",
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Git clone error: {e}")
            return {
                "status": "error",
                "error_type": "git_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
    
    def _git_pull(self, repo_dir: str, branch: str) -> Dict[str, Any]:
        """Execute git pull command"""
        try:
            cmd = ['git', '-C', repo_dir, 'pull', 'origin', branch]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Git pull failed: {result.stderr}")
                return {
                    "status": "error",
                    "error_type": "git_pull_failed",
                    "message": result.stderr,
                    "timestamp": get_timestamp()
                }
            
            logger.info(f"Repository updated at {repo_dir}")
            
            return {
                "status": "success",
                "action": "updated",
                "repository": repo_dir,
                "branch": branch,
                "timestamp": get_timestamp()
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Git pull timed out")
            return {
                "status": "error",
                "error_type": "timeout",
                "message": "Git pull operation timed out",
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Git pull error: {e}")
            return {
                "status": "error",
                "error_type": "git_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
    
    def detect_openclaw_skills(self, repo_dir: str) -> List[Dict[str, str]]:
        """
        Auto-detect OpenClaw skills in the repository.
        
        Args:
            repo_dir: Repository directory
            
        Returns:
            List of detected skills with their paths
        """
        skills = []
        
        try:
            for root, dirs, files in os.walk(repo_dir):
                # Check if directory contains OpenClaw skill markers
                if all(marker in files for marker in self.OPENCLAW_SKILL_MARKERS):
                    rel_path = os.path.relpath(root, repo_dir)
                    skill_name = os.path.basename(root)
                    
                    skills.append({
                        "name": skill_name,
                        "path": rel_path,
                        "full_path": root,
                        "config": os.path.join(root, 'config.yaml'),
                        "skill_file": os.path.join(root, 'skill.py'),
                        "documentation": os.path.join(root, 'SKILL.md')
                    })
                    
                    logger.info(f"Detected OpenClaw skill: {skill_name}")
        
        except Exception as e:
            logger.error(f"Error detecting skills: {e}")
        
        return skills
    
    def install_skills(self, source_dir: str, target_dir: str = None) -> Dict[str, Any]:
        """
        Install detected OpenClaw skills.
        
        Args:
            source_dir: Directory containing skills
            target_dir: Target installation directory (default: ./skills/)
            
        Returns:
            Installation status and results
        """
        try:
            if target_dir is None:
                target_dir = os.path.join(os.getcwd(), 'skills')
            
            target_dir = validate_file_path(target_dir)
            os.makedirs(target_dir, exist_ok=True)
            
            logger.info(f"Detecting skills in {source_dir}...")
            detected_skills = self.detect_openclaw_skills(source_dir)
            
            if not detected_skills:
                logger.warning("No OpenClaw skills detected")
                return {
                    "status": "warning",
                    "message": "No OpenClaw skills detected in repository",
                    "skills_installed": [],
                    "timestamp": get_timestamp()
                }
            
            installed_skills = []
            failed_skills = []
            
            for skill in detected_skills:
                try:
                    logger.info(f"Installing skill: {skill['name']}")
                    
                    # Create backup if skill exists
                    skill_target = os.path.join(target_dir, skill['name'])
                    if os.path.exists(skill_target) and self.backup_enabled:
                        backup_dir = f"{skill_target}.backup.{get_timestamp()}"
                        shutil.copytree(skill_target, backup_dir)
                        logger.info(f"Backed up existing skill to {backup_dir}")
                    
                    # Copy skill to target directory
                    if os.path.exists(skill_target):
                        shutil.rmtree(skill_target)
                    
                    shutil.copytree(skill['full_path'], skill_target)
                    logger.info(f"Skill installed: {skill['name']} -> {skill_target}")
                    
                    installed_skills.append({
                        "name": skill['name'],
                        "path": skill_target,
                        "status": "installed"
                    })
                
                except Exception as e:
                    logger.error(f"Failed to install skill {skill['name']}: {e}")
                    failed_skills.append({
                        "name": skill['name'],
                        "error": str(e)
                    })
            
            safe_log_api_call(
                "GitHub",
                "install_skills",
                "success",
                {"installed": len(installed_skills), "failed": len(failed_skills)}
            )
            
            return {
                "status": "success" if not failed_skills else "partial",
                "skills_detected": len(detected_skills),
                "skills_installed": installed_skills,
                "skills_failed": failed_skills,
                "target_directory": target_dir,
                "timestamp": get_timestamp()
            }
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            safe_log_api_call("GitHub", "install_skills", "error")
            return {
                "status": "error",
                "error_type": "installation_failed",
                "message": str(e),
                "timestamp": get_timestamp()
            }
    
    def get_google_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """
        Generate Google OAuth authorization URL (for optional authentication).
        
        Args:
            state: CSRF protection state token
            
        Returns:
            OAuth URL and state
        """
        try:
            if not self.google_oauth.is_configured():
                return {
                    "status": "warning",
                    "message": "Google OAuth is not configured",
                    "oauth_available": False,
                    "timestamp": get_timestamp()
                }
            
            if state:
                state = validate_oauth_state(state)
            else:
                import secrets
                state = secrets.token_urlsafe(32)
            
            auth_url = self.google_oauth.get_authorization_url(state)
            
            logger.info("Generated Google OAuth authorization URL")
            
            return {
                "status": "success",
                "oauth_available": True,
                "authorization_url": auth_url,
                "state": state,
                "timestamp": get_timestamp()
            }
        
        except SecurityError as e:
            logger.error(f"OAuth error: {e}")
            return {
                "status": "error",
                "error_type": "oauth_error",
                "message": str(e),
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "status": "error",
                "error_type": "unexpected",
                "message": str(e),
                "timestamp": get_timestamp()
            }


def execute_skill(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the GitHub Installer skill.
    
    Args:
        parameters: OpenClaw parameters containing:
            - repository_url: GitHub repository URL (required)
            - branch: Git branch to use (default: main)
            - action: 'clone' or 'install_skills' (default: both)
            - target_dir: Installation directory (optional)
            - google_auth_required: Enable Google OAuth (default: false)
    
    Returns:
        Result dictionary with installation status
    """
    try:
        if not parameters or 'repository_url' not in parameters:
            return {
                "status": "error",
                "error_type": "missing_parameter",
                "message": "Missing required parameter: 'repository_url'",
                "timestamp": get_timestamp()
            }
        
        installer = GitHubInstaller()
        
        repo_url = parameters['repository_url']
        branch = parameters.get('branch', 'main')
        action = parameters.get('action', 'clone_and_install')
        target_dir = parameters.get('target_dir', None)
        google_auth = parameters.get('google_auth_required', False)
        
        # Get Google OAuth if requested
        google_oauth_result = None
        if google_auth:
            logger.info("Google OAuth requested")
            google_oauth_result = installer.get_google_oauth_url()
        
        # Clone repository
        clone_result = installer.clone_repository(repo_url, branch, target_dir)
        if clone_result['status'] != 'success':
            return clone_result
        
        cloned_dir = clone_result['target_dir']
        
        # Install skills if action is 'clone_and_install' or 'install_skills'
        if action in ['clone_and_install', 'install_skills']:
            install_result = installer.install_skills(cloned_dir, target_dir)
            
            result = {
                "status": install_result['status'],
                "repository": repo_url,
                "branch": branch,
                "clone_status": clone_result['action'],
                "repository_path": cloned_dir,
                "installation": install_result,
                "timestamp": get_timestamp()
            }
            
            if google_oauth_result:
                result['google_oauth'] = google_oauth_result
            
            return result
        
        # Just return clone result if action is 'clone'
        return clone_result
    
    except SecurityError as e:
        logger.error(f"Security error in skill execution: {e}")
        return {
            "status": "error",
            "error_type": "security_error",
            "message": str(e),
            "timestamp": get_timestamp()
        }
    except Exception as e:
        logger.error(f"Unexpected error in skill execution: {e}")
        return {
            "status": "error",
            "error_type": "execution_error",
            "message": str(e),
            "timestamp": get_timestamp()
        }


if __name__ == "__main__":
    # Test execution
    test_params = {
        "repository_url": "https://github.com/Cenralsolution/clawskills",
        "branch": "main",
        "action": "clone"
    }
    result = execute_skill(test_params)
    print(json.dumps(result, indent=2))
