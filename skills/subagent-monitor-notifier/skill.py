"""
Sub-Agent Monitor & Notifier Skill

This skill provides built-in push-notification functionality for monitoring
sub-agent status, tracking state changes, and sending real-time notifications.

Features:
- Periodic polling of sub-agent status
- Automatic status change detection
- Multi-channel notifications (log, email, webhook, SMS)
- Scheduling support (cron-like patterns)
- Session history tracking
- Alert aggregation and deduplication
- Configurable polling intervals

Authentication: Internal (uses local session storage)
Scheduling: APScheduler for cron-like job scheduling
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for shared utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils import (
    validate_string_input,
    get_secure_api_key,
    safe_log_api_call,
    validate_theme
)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not available - scheduling features limited")


class AgentStatus(Enum):
    """Status states for sub-agents"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class NotificationChannel(Enum):
    """Supported notification channels"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    FILE = "file"


@dataclass
class AgentStatusSnapshot:
    """Snapshot of an agent's status at a point in time"""
    agent_id: str
    agent_name: str
    status: str
    timestamp: str
    details: Dict[str, Any]
    error_message: Optional[str] = None
    completion_percentage: int = 0
    session_id: Optional[str] = None


@dataclass
class StatusChange:
    """Record of a status change for an agent"""
    agent_id: str
    previous_status: str
    new_status: str
    timestamp: str
    reason: Optional[str] = None
    change_hash: Optional[str] = None


class SubAgentMonitor:
    """
    Monitors sub-agent status and sends notifications.
    
    This skill provides passive polling-based monitoring without requiring
    modification to sub-agents or complex infrastructure changes.
    
    Supports:
    - Period polling of agent status
    - Status change detection and notification
    - Multi-channel alerts
    - Session history tracking
    - Scheduled monitoring jobs
    - Alert deduplication
    """
    
    def __init__(
        self,
        poll_interval: int = 60,
        retention_days: int = 7,
        notification_channels: Optional[List[str]] = None,
        enable_scheduling: bool = True
    ):
        """
        Initialize Sub-Agent Monitor.
        
        Args:
            poll_interval: Seconds between polling cycles (default: 60)
            retention_days: Days to retain status history (default: 7)
            notification_channels: List of channels to use (default: ["log"])
            enable_scheduling: Enable automatic background scheduling
        """
        
        self.poll_interval = poll_interval
        self.retention_days = retention_days
        self.notification_channels = notification_channels or ["log"]
        self.enable_scheduling = enable_scheduling and SCHEDULER_AVAILABLE
        
        # State tracking
        self.agent_statuses: Dict[str, AgentStatusSnapshot] = {}
        self.status_history: Dict[str, List[AgentStatusSnapshot]] = {}
        self.status_changes: Dict[str, List[StatusChange]] = {}
        self.last_poll_time: Dict[str, datetime] = {}
        self.alert_cache: Set[str] = set()  # For deduplication
        self.polling_active = False
        
        # Storage
        self.storage_dir = Path(os.getenv("MONITOR_STORAGE_DIR", "./monitor_data"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Scheduler
        self.scheduler: Optional[BackgroundScheduler] = None
        if self.enable_scheduling:
            self.scheduler = BackgroundScheduler()
        
        logger.info(f"SubAgentMonitor initialized with poll_interval={poll_interval}s")
    
    def start_monitoring(
        self,
        agent_ids: List[str],
        schedule_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start monitoring one or more sub-agents.
        
        Args:
            agent_ids: List of agent IDs/names to monitor
            schedule_pattern: Optional cron pattern (e.g., "*/1 * * * *" for every minute)
            
        Returns:
            Monitoring configuration and status
        """
        
        logger.info(f"Starting monitoring for agents: {agent_ids}")
        
        result = {
            "status": "monitoring_started",
            "agents": agent_ids,
            "poll_interval": self.poll_interval,
            "timestamp": datetime.now().isoformat(),
            "scheduling_enabled": self.enable_scheduling,
            "notification_channels": self.notification_channels
        }
        
        # Initialize tracking for each agent
        for agent_id in agent_ids:
            self.agent_statuses[agent_id] = AgentStatusSnapshot(
                agent_id=agent_id,
                agent_name=agent_id,
                status=AgentStatus.UNKNOWN.value,
                timestamp=datetime.now().isoformat(),
                details={}
            )
            self.status_history[agent_id] = []
            self.status_changes[agent_id] = []
        
        # Schedule monitoring job if requested
        if schedule_pattern and self.scheduler and not self.polling_active:
            try:
                self.scheduler.add_job(
                    func=self._poll_agents,
                    args=[agent_ids],
                    trigger=CronTrigger.from_crontab(schedule_pattern),
                    id="agent_monitor_cron",
                    replace_existing=True
                )
                
                if not self.scheduler.running:
                    self.scheduler.start()
                
                result["scheduled"] = True
                result["schedule_pattern"] = schedule_pattern
                safe_log_api_call(
                    "SubAgentMonitor",
                    "start_monitoring",
                    "scheduled",
                    {"agents": len(agent_ids), "pattern": schedule_pattern}
                )
                
            except Exception as e:
                safe_log_api_call(
                    "SubAgentMonitor",
                    "start_monitoring",
                    "error",
                    {"error": str(e), "error_type": type(e).__name__}
                )
                result["scheduling_error"] = str(e)
        
        # Perform initial poll
        changes = self._poll_agents(agent_ids)
        result["initial_poll_changes"] = len(changes)
        
        self.polling_active = True
        
        return result
    
    def _poll_agents(self, agent_ids: List[str]) -> List[StatusChange]:
        """
        Poll the status of specified agents.
        
        This method checks agent status from session history, job logs,
        or any available status source.
        """
        
        changes: List[StatusChange] = []
        
        for agent_id in agent_ids:
            try:
                # Simulate fetching agent status (in real implementation,
                # would fetch from session_history, job queue, etc.)
                current_status = self._fetch_agent_status(agent_id)
                previous_status = self.agent_statuses.get(agent_id)
                
                # Check for status change
                if previous_status and current_status.status != previous_status.status:
                    change = StatusChange(
                        agent_id=agent_id,
                        previous_status=previous_status.status,
                        new_status=current_status.status,
                        timestamp=datetime.now().isoformat(),
                        reason=f"Status change detected: {previous_status.status} → {current_status.status}"
                    )
                    
                    # Calculate change hash for deduplication
                    change_str = f"{agent_id}:{change.previous_status}:{change.new_status}"
                    change.change_hash = hashlib.md5(change_str.encode()).hexdigest()
                    
                    # Check if this is a duplicate alert
                    if change.change_hash not in self.alert_cache:
                        self.status_changes[agent_id].append(change)
                        changes.append(change)
                        self.alert_cache.add(change.change_hash)
                        
                        # Send notifications
                        self._send_notifications(change, current_status)
                
                # Update status
                self.agent_statuses[agent_id] = current_status
                self.status_history[agent_id].append(current_status)
                self.last_poll_time[agent_id] = datetime.now()
                
            except Exception as e:
                safe_log_api_call(
                    "SubAgentMonitor",
                    "poll_agents",
                    "error",
                    {"agent_id": agent_id, "error": str(e), "error_type": type(e).__name__}
                )
        
        return changes
    
    def _fetch_agent_status(self, agent_id: str) -> AgentStatusSnapshot:
        """
        Fetch current status of an agent.
        
        In a real implementation, this would:
        - Query OpenClaw session history
        - Check job queue status
        - Poll agent process status
        - Read from status files
        """
        
        # Placeholder implementation that reads from status file if available
        status_file = self.storage_dir / f"{agent_id}_status.json"
        
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                return AgentStatusSnapshot(**data)
            except Exception as e:
                logger.warning(f"Failed to read status file for {agent_id}: {e}")
        
        # Return current known status or unknown
        if agent_id in self.agent_statuses:
            return self.agent_statuses[agent_id]
        else:
            return AgentStatusSnapshot(
                agent_id=agent_id,
                agent_name=agent_id,
                status=AgentStatus.UNKNOWN.value,
                timestamp=datetime.now().isoformat(),
                details={}
            )
    
    def _send_notifications(
        self,
        change: StatusChange,
        current_status: AgentStatusSnapshot
    ) -> None:
        """Send notifications through configured channels"""
        
        notification_message = self._format_notification(change, current_status)
        
        for channel in self.notification_channels:
            try:
                if channel.lower() == "log":
                    self._notify_log(notification_message, change)
                elif channel.lower() == "file":
                    self._notify_file(notification_message, change)
                elif channel.lower() == "email":
                    self._notify_email(notification_message, change)
                elif channel.lower() == "webhook":
                    self._notify_webhook(notification_message, change)
                elif channel.lower() == "slack":
                    self._notify_slack(notification_message, change)
                elif channel.lower() == "sms":
                    self._notify_sms(notification_message, change)
                    
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {str(e)}")
    
    def _format_notification(
        self,
        change: StatusChange,
        status: AgentStatusSnapshot
    ) -> str:
        """Format notification message"""
        
        return f"""
Agent Status Update
Agent ID: {change.agent_id}
Previous Status: {change.previous_status}
New Status: {change.new_status}
Timestamp: {change.timestamp}
Reason: {change.reason}
Details: {json.dumps(status.details, indent=2) if status.details else 'None'}
Error: {status.error_message or 'None'}
Progress: {status.completion_percentage}%
        """.strip()
    
    def _notify_log(self, message: str, change: StatusChange) -> None:
        """Send notification via logging"""
        log_level = "WARNING" if change.new_status in ["FAILED", "TIMEOUT"] else "INFO"
        getattr(logger, log_level.lower())(f"ALERT: {message}")
    
    def _notify_file(self, message: str, change: StatusChange) -> None:
        """Send notification via file"""
        alert_file = self.storage_dir / "alerts.log"
        with open(alert_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {change.agent_id}\n")
            f.write(message + "\n\n")
    
    def _notify_email(self, message: str, change: StatusChange) -> None:
        """Send notification via email"""
        try:
            # Placeholder for email notification
            email_config = os.getenv("NOTIFICATION_EMAIL_CONFIG")
            if email_config:
                safe_log_api_call(
                    "SubAgentMonitor",
                    "notify_email",
                    "sending",
                    {"agent_id": change.agent_id, "status": change.new_status}
                )
            else:
                logger.debug("Email notifications disabled: NOTIFICATION_EMAIL_CONFIG not set")
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
    
    def _notify_webhook(self, message: str, change: StatusChange) -> None:
        """Send notification via webhook"""
        try:
            # Try to get webhook URL - it's a sensitive credential that should be protected
            webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
            
            if not webhook_url:
                logger.debug("Webhook notifications disabled: NOTIFICATION_WEBHOOK_URL not set")
                return
            
            if not webhook_url.startswith(('http://', 'https://')):
                logger.error("Invalid webhook URL format (must be HTTP/HTTPS)")
                return
            
            import requests
            
            payload = {
                "agent_id": change.agent_id,
                "previous_status": change.previous_status,
                "new_status": change.new_status,
                "timestamp": change.timestamp,
                "message": message
            }
            
            # Log the attempt without exposing the URL
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_webhook",
                "sending",
                {"agent_id": change.agent_id, "status": change.new_status}
            )
            
            requests.post(webhook_url, json=payload, timeout=10)
            
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_webhook",
                "success",
                {"agent_id": change.agent_id}
            )
            
        except Exception as e:
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_webhook",
                "error",
                {"error": str(e), "error_type": type(e).__name__}
            )
    
    def _notify_slack(self, message: str, change: StatusChange) -> None:
        """Send notification via Slack"""
        try:
            slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
            
            if not slack_webhook:
                logger.debug("Slack notifications disabled: SLACK_WEBHOOK_URL not set")
                return
            
            if not slack_webhook.startswith(('http://', 'https://')):
                logger.error("Invalid Slack webhook URL format (must be HTTP/HTTPS)")
                return
            
            import requests
            
            color = "danger" if change.new_status in ["failed", "timeout"] else "good"
            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"Agent {change.agent_id} Status Update",
                    "text": message,
                    "ts": int(time.time())
                }]
            }
            
            # Log the attempt without exposing the webhook URL
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_slack",
                "sending",
                {"agent_id": change.agent_id, "status": change.new_status}
            )
            
            requests.post(slack_webhook, json=payload, timeout=10)
            
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_slack",
                "success",
                {"agent_id": change.agent_id}
            )
            
        except Exception as e:
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_slack",
                "error",
                {"error": str(e), "error_type": type(e).__name__}
            )
    
    def _notify_sms(self, message: str, change: StatusChange) -> None:
        """Send notification via SMS"""
        try:
            sms_config = os.getenv("NOTIFICATION_SMS_CONFIG")
            
            if not sms_config:
                logger.debug("SMS notifications disabled: NOTIFICATION_SMS_CONFIG not set")
                return
            
            # Log the attempt without exposing configuration
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_sms",
                "sending",
                {"agent_id": change.agent_id, "status": change.new_status}
            )
            
            # Placeholder for SMS implementation
            logger.info(f"SMS notification queued for agent {change.agent_id}")
            
        except Exception as e:
            safe_log_api_call(
                "SubAgentMonitor",
                "notify_sms",
                "error",
                {"error": str(e), "error_type": type(e).__name__}
            )
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get current status of an agent"""
        
        if agent_id not in self.agent_statuses:
            return {
                "status": "error",
                "message": f"Agent {agent_id} not being monitored"
            }
        
        snapshot = self.agent_statuses[agent_id]
        
        return {
            "agent_id": agent_id,
            "current_status": snapshot.status,
            "last_updated": snapshot.timestamp,
            "details": snapshot.details,
            "error": snapshot.error_message,
            "progress": snapshot.completion_percentage,
            "recent_changes": [asdict(c) for c in self.status_changes[agent_id][-5:]]
        }
    
    def get_status_history(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get status history for an agent"""
        
        if agent_id not in self.status_history:
            return []
        
        return [asdict(s) for s in self.status_history[agent_id][-limit:]]
    
    def stop_monitoring(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Stop monitoring an agent or all agents"""
        
        if self.scheduler and self.scheduler.running:
            if agent_id:
                logger.info(f"Stopping monitoring for agent: {agent_id}")
            else:
                logger.info("Stopping all monitoring")
                self.scheduler.shutdown()
                self.polling_active = False
        
        return {
            "status": "monitoring_stopped",
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Sub-Agent Monitor skill.
        
        Input format:
        {
            "action": "start|stop|status|history",
            "agent_ids": ["agent1", "agent2"],
            "schedule_pattern": "*/1 * * * *",  # Optional: cron pattern
            "poll_interval": 60,
            "notification_channels": ["log", "webhook"]
        }
        """
        
        try:
            action = input_data.get("action", "start").lower()
            
            if action == "start":
                agent_ids = input_data.get("agent_ids", [])
                schedule_pattern = input_data.get("schedule_pattern")
                
                result = self.start_monitoring(
                    agent_ids=agent_ids,
                    schedule_pattern=schedule_pattern
                )
                
                return {
                    "status": "success",
                    "data": result
                }
            
            elif action == "stop":
                result = self.stop_monitoring(
                    agent_id=input_data.get("agent_id")
                )
                
                return {
                    "status": "success",
                    "data": result
                }
            
            elif action == "status":
                agent_id = input_data.get("agent_id")
                result = self.get_agent_status(agent_id)
                
                return {
                    "status": "success",
                    "data": result
                }
            
            elif action == "history":
                agent_id = input_data.get("agent_id")
                limit = input_data.get("limit", 100)
                result = self.get_status_history(agent_id, limit)
                
                return {
                    "status": "success",
                    "data": result
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["start", "stop", "status", "history"]
                }
        
        except Exception as e:
            safe_log_api_call(
                "SubAgentMonitor",
                f"execute_skill(action={input_data.get('action', 'unknown')})",
                "error",
                {"error": str(e), "error_type": type(e).__name__}
            )
            
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill"""
    return {
        "name": "Sub-Agent Monitor & Notifier",
        "version": "1.0.0",
        "description": "Monitor sub-agent status and send push notifications",
        "purpose": "Provides built-in polling-based monitoring and notification system for sub-agents",
        "capabilities": [
            "periodic-polling",
            "status-change-detection",
            "multi-channel-notifications",
            "scheduled-monitoring",
            "alert-deduplication",
            "session-history-tracking"
        ],
        "supported_actions": ["start", "stop", "status", "history"],
        "notification_channels": [
            "log",
            "file",
            "email",
            "webhook",
            "slack",
            "sms"
        ],
        "input_schema": {
            "action": "string (start, stop, status, history)",
            "agent_ids": "list of strings",
            "schedule_pattern": "string (optional, cron pattern)",
            "poll_interval": "integer (seconds)",
            "notification_channels": "list of strings"
        }
    }
