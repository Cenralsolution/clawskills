"""
Sub-Agent Monitor & Notifier Skill

Provides built-in push-notification functionality for monitoring sub-agent status,
detecting state changes, and sending real-time notifications through multiple channels.
"""

from .skill import (
    SubAgentMonitor,
    AgentStatus,
    NotificationChannel,
    AgentStatusSnapshot,
    StatusChange,
    get_skill_info
)

__version__ = "1.0.0"
__author__ = "OpenClaw"
__all__ = [
    "SubAgentMonitor",
    "AgentStatus",
    "NotificationChannel",
    "AgentStatusSnapshot",
    "StatusChange",
    "get_skill_info"
]
