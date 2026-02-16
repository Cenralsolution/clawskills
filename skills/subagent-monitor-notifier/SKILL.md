# Sub-Agent Monitor & Notifier Skill

**Version:** 1.0.0  
**Category:** Orchestration  
**Purpose:** Monitor sub-agent status and send push notifications  
**Status:** Production-ready

## Overview

The Sub-Agent Monitor & Notifier skill solves the critical problem of monitoring sub-agents without requiring modifications to the sub-agents themselves. It provides **built-in push-notification functionality** through polling-based monitoring, supporting multiple notification channels and scheduling methods.

### Problem Statement

OpenClaw's sub-agent system has no built-in push-notification mechanism. When a sub-agent completes, fails, or times out, there is no automatic way to:
- Detect status changes in real-time
- Send notifications to multiple channels
- Track status history
- Trigger downstream workflows

This skill provides three solutions:
1. **Polling Loop** - Active monitoring with configurable intervals
2. **Cron Job Scheduling** - Automated monitoring on a schedule
3. **Alert Aggregation** - Batch notifications to reduce noise

---

## Features

### ✅ Core Capabilities

- **Periodic Polling**: Monitor agent status at configurable intervals
- **Status Change Detection**: Automatic detection of status transitions
- **Multi-Channel Notifications**: Email, Webhook, Slack, SMS, Log, File
- **Scheduled Monitoring**: Cron-like scheduling with APScheduler
- **Session History Tracking**: Maintain historical records of agent activity
- **Alert Deduplication**: Prevent duplicate notifications using content hashing
- **Alert Aggregation**: Batch multiple alerts into single notification
- **Error Handling**: Robust error handling with retry logic
- **Security**: Zero-trust input validation and secure credential handling
- **Audit Trail**: Comprehensive logging of all monitoring activities

### 🎯 Monitoring Coverage

Can monitor agents from multiple sources:
- **OpenClaw Session History** - Track session-based agents
- **Job Queue Status** - Monitor queued job execution
- **Process Logs** - Parse log files for status information
- **Status Files** - Read JSON/log-based status files
- **HTTP Endpoints** - Poll status from agent APIs

---

## Installation

### Prerequisites
- Python 3.8+
- OpenClaw Framework v2.0+
- (Optional) APScheduler for scheduled monitoring

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or with optional scheduling support
pip install -r requirements.txt
pip install apscheduler
```

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Storage Configuration
MONITOR_STORAGE_DIR=./monitor_data

# Email Notifications
NOTIFICATION_EMAIL_USER=your-email@gmail.com
NOTIFICATION_EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL_FROM=alerts@company.com
NOTIFICATION_EMAIL_TO=admin@company.com,devops@company.com

# Webhook Notifications
NOTIFICATION_WEBHOOK_URL=https://your-api.com/webhooks/alerts

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# SMS Notifications (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
SMS_FROM_NUMBER=+1234567890
SMS_TO_NUMBERS=+9876543210,+9876543211
```

---

## Usage

### Basic Usage

#### 1. Starting Monitoring

```python
from skills.subagent_monitor_notifier import SubAgentMonitor

# Create monitor instance
monitor = SubAgentMonitor(
    poll_interval=60,  # Check every 60 seconds
    retention_days=7,  # Keep 7 days of history
    notification_channels=["log", "webhook", "slack"]
)

# Start monitoring specific agents
result = monitor.start_monitoring(
    agent_ids=["agent_1", "agent_2", "agent_3"],
    schedule_pattern="*/5 * * * *"  # Every 5 minutes
)

print(result)
# Output:
# {
#   "status": "monitoring_started",
#   "agents": ["agent_1", "agent_2", "agent_3"],
#   "poll_interval": 60,
#   "timestamp": "2024-01-15T10:30:00",
#   "scheduling_enabled": true,
#   "notification_channels": ["log", "webhook", "slack"],
#   "scheduled": true,
#   "schedule_pattern": "*/5 * * * *",
#   "initial_poll_changes": 0
# }
```

#### 2. Using Skill Interface

```python
skill_input = {
    "action": "start",
    "agent_ids": ["agent_1", "agent_2"],
    "poll_interval": 60,
    "notification_channels": ["log", "webhook"],
    "schedule_pattern": "*/5 * * * *"
}

monitor = SubAgentMonitor()
result = monitor.execute_skill(skill_input)
```

#### 3. Getting Agent Status

```python
# Get current status of an agent
status = monitor.get_agent_status("agent_1")

print(status)
# Output:
# {
#   "agent_id": "agent_1",
#   "current_status": "running",
#   "last_updated": "2024-01-15T10:30:00",
#   "details": {"job_id": "job_abc123", "progress": 45},
#   "error": null,
#   "progress": 45,
#   "recent_changes": [
#     {
#       "agent_id": "agent_1",
#       "previous_status": "pending",
#       "new_status": "running",
#       "timestamp": "2024-01-15T10:25:00",
#       "reason": "Status change detected: pending → running"
#     }
#   ]
# }
```

#### 4. Retrieving Status History

```python
# Get historical status records
history = monitor.get_status_history("agent_1", limit=50)

for record in history[-5:]:  # Last 5 records
    print(f"{record['timestamp']}: {record['status']}")

# Output:
# 2024-01-15T10:05:00: pending
# 2024-01-15T10:10:00: running
# 2024-01-15T10:20:00: running
# 2024-01-15T10:25:00: completed
```

#### 5. Stopping Monitoring

```python
# Stop monitoring a specific agent
monitor.stop_monitoring("agent_1")

# Stop all monitoring
monitor.stop_monitoring()
```

---

## Scheduling Patterns

### Cron Format

SubAgentMonitor uses standard cron patterns with APScheduler:

```
minute hour day month day_of_week
0-59   0-23  1-31  1-12   0-6 (0=Sunday)
```

**Common Patterns:**

| Pattern | Frequency | Use Case |
|---------|-----------|----------|
| `*/1 * * * *` | Every 1 minute | Urgent/critical agents |
| `*/5 * * * *` | Every 5 minutes | Standard monitoring |
| `*/10 * * * *` | Every 10 minutes | Background jobs |
| `0 * * * *` | Every hour | Batch processes |
| `0 0 * * *` | Daily at midnight | Daily reports |
| `0 */6 * * *` | Every 6 hours | Long-running tasks |
| `0 9-17 * * 1-5` | Every hour (9am-6pm, weekdays only) | Business hours |

---

## Notification Channels

### 1. Log Channel

Sends alerts to Python logging system:

```python
monitor = SubAgentMonitor(notification_channels=["log"])

# Output to console/log files:
# 2024-01-15 10:30:00 - SubAgentMonitor - WARNING - ALERT: Agent Status Update...
```

**Configuration:**
```yaml
notifications:
  log:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

### 2. File Channel

Appends alerts to a dedicated alert file:

```bash
# Creates ./monitor_data/alerts.log
# Format: timestamp - agent_id - Alert details
2024-01-15T10:30:00 - agent_1
Agent Status Update
Agent ID: agent_1
Previous Status: running
New Status: completed
...
```

**Configuration:**
```yaml
notifications:
  file:
    enabled: true
    alert_file: "./monitor_data/alerts.log"
    archive_old_logs: true
    log_rotation_days: 7
```

---

### 3. Email Channel

Sends email notifications for status changes:

**Setup:**

```bash
# Environment variables
export NOTIFICATION_EMAIL_USER=alerts@gmail.com
export NOTIFICATION_EMAIL_PASSWORD=app-specific-password
```

**Configuration:**
```yaml
notifications:
  email:
    enabled: true
    server: "smtp.gmail.com"
    port: 587
    use_tls: true
    from_address: "alerts@company.com"
    to_addresses:
      - "admin@example.com"
      - "devops@example.com"
    templates:
      subject: "Alert: Agent {agent_id} Status Changed to {new_status}"
```

**Example Email:**
```
Subject: Alert: Agent agent_1 Status Changed to completed

Agent Status Update
Agent ID: agent_1
Previous Status: running
New Status: completed
Timestamp: 2024-01-15T10:30:00
Progress: 100%
```

---

### 4. Webhook Channel

Sends HTTP POST requests to your API endpoint:

**Setup:**

```bash
export NOTIFICATION_WEBHOOK_URL=https://api.company.com/webhooks/alerts
```

**Payload Format:**
```json
{
  "agent_id": "agent_1",
  "previous_status": "running",
  "new_status": "completed",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Agent Status Update\nAgent ID: agent_1\n...",
  "details": {
    "job_id": "job_abc123",
    "progress": 100
  }
}
```

**Handler Example:**
```python
@app.post("/webhooks/alerts")
async def handle_alert(event: dict):
    agent_id = event["agent_id"]
    new_status = event["new_status"]
    
    # Process alert: trigger downstream workflow, update dashboard, etc.
    if new_status == "failed":
        await trigger_escalation(agent_id)
    elif new_status == "completed":
        await trigger_downstream_tasks(agent_id)
    
    return {"status": "received"}
```

---

### 5. Slack Channel

Sends formatted messages to Slack channels:

**Setup:**

```bash
# Create Incoming Webhook in Slack
# https://api.slack.com/messaging/webhooks
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Configuration:**
```yaml
notifications:
  slack:
    enabled: true
    mention_on_failure: true
    failure_mentions:
      - "@devops"
      - "@oncall"
    status_colors:
      completed: "#36a64f"  # Green
      running: "#0099ff"    # Blue
      failed: "#ff0000"     # Red
```

**Slack Message:**
```
User: OpenClaw Monitor
Alert: Agent agent_1 Status Changed

Agent Status Update
Agent ID: agent_1
Previous Status: running
New Status: completed
Timestamp: 2024-01-15T10:30:00
Progress: 100%
```

---

### 6. SMS Channel

Sends SMS alerts for critical events:

**Setup (Twilio):**

```bash
export SMS_PROVIDER=twilio
export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
export TWILIO_AUTH_TOKEN=your-auth-token
```

**Configuration:**
```yaml
notifications:
  sms:
    enabled: true
    provider: "twilio"
    alert_numbers:
      - "+1234567890"
      - "+9876543210"
```

---

## Alert Severity & Escalation

### Severity Levels

```yaml
alerts:
  severity_levels:
    critical:
      statuses: ["failed", "timeout"]
      channels: ["log", "email", "slack", "sms"]
      priority: 1
    
    warning:
      statuses: ["pending", "cancelled"]
      channels: ["log", "file", "slack"]
      priority: 2
    
    info:
      statuses: ["running", "completed"]
      channels: ["log", "file"]
      priority: 3
```

### Escalation Rules

```yaml
alerts:
  thresholds:
    # Escalate after 3 consecutive failures
    failure_escalation_threshold: 3
    # Within this time window (seconds)
    failure_window: 300
```

---

## Integration with Skills

### 1. Music Generation Orchestrator

Monitor music generation tasks:

```python
# In music-orchestrator/skill.py
from skills.subagent_monitor_notifier import SubAgentMonitor

# After spawning music generation sub-agents
monitor = SubAgentMonitor(
    poll_interval=5,  # Check every 5 seconds
    notification_channels=["log", "webhook"]
)

# Monitor the sub-agents
monitor.start_monitoring(
    agent_ids=["music_gen_aiva", "music_gen_mubert"],
    schedule_pattern="*/1 * * * *"  # Every minute
)
```

### 2. GitHub Integration

Auto-create issues for critical failures:

```python
# Configuration enables automatic issue creation
integration:
  github_integration:
    enabled: true
    trigger_on: "critical_failure"
    auto_create_issues: true
    repo_owner: "company"
    repo_name: "openclawskills"
```

### 3. ChatGPT Summarization

Summarize alerts using ChatGPT:

```python
# Enable in config.yaml
integration:
  skills:
    chatgpt_summarization:
      enabled: true
      trigger_on: "multiple_failures"
```

---

## Configuration Examples

### Example 1: Minimal Setup

```python
# Basic monitoring with default settings
monitor = SubAgentMonitor()
monitor.start_monitoring(agent_ids=["agent_1"])
```

### Example 2: Comprehensive Setup

```python
# Full-featured monitoring
monitor = SubAgentMonitor(
    poll_interval=30,
    retention_days=14,
    notification_channels=["log", "email", "webhook", "slack"],
    enable_scheduling=True
)

result = monitor.start_monitoring(
    agent_ids=["agent_1", "agent_2", "agent_3"],
    schedule_pattern="*/5 * * * *"
)

# Verify monitoring is active
status = monitor.get_agent_status("agent_1")
print(f"Monitoring {status['agent_id']}: {status['current_status']}")

# Keep track of history
history = monitor.get_status_history("agent_1", limit=100)
print(f"Last 100 status records: {len(history)}")
```

### Example 3: Custom Notification Logic

```python
# Create custom monitor with selective notifications
monitor = SubAgentMonitor(notification_channels=["webhook"])

# Only notify on failures
monitor.start_monitoring(
    agent_ids=["critical_agent"],
    schedule_pattern="*/1 * * * *"
)

# Manually prevent notification for non-critical agents
monitor.start_monitoring(
    agent_ids=["background_agent"],
    schedule_pattern="0 * * * *"  # Only hourly
)
```

### Example 4: Integrating with Music Orchestrator

```python
# In orchestra skill
from skills.subagent_monitor_notifier import SubAgentMonitor

def orchestrate_music_generation(theme: str):
    # Generate prompt and spawn music generation sub-agents
    agents = spawn_music_agents(theme)
    
    # Monitor the sub-agents
    monitor = SubAgentMonitor(
        poll_interval=10,
        notification_channels=["log", "webhook"]
    )
    
    monitor.start_monitoring(
        agent_ids=agents,
        schedule_pattern="*/2 * * * *"
    )
    
    # Wait for all agents to complete
    completed = 0
    while completed < len(agents):
        for agent_id in agents:
            status = monitor.get_agent_status(agent_id)
            if status["current_status"] == "completed":
                completed += 1
        
        time.sleep(10)
```

---

## Advanced Patterns

### Pattern 1: Alert Aggregation

Batch multiple alerts to reduce notification noise:

```yaml
notifications:
  aggregation:
    enabled: true
    batch_window: 60  # 60 seconds
    batch_threshold: 3  # Minimum 3 changes to batch
```

This batches multiple status changes within 60 seconds into a single notification if there are 3+ changes.

---

### Pattern 2: Rate Limiting

Prevent alert storm during system outages:

```yaml
security:
  rate_limiting:
    enabled: true
    max_alerts_per_minute: 10  # Max 10 alerts per agent per minute
```

---

### Pattern 3: Time Window Monitoring

Monitor only during business hours:

```python
# Cron pattern: 0 9-17 * * 1-5
# = Every hour, 9am-6pm, Monday-Friday
monitor.start_monitoring(
    agent_ids=["business_agent"],
    schedule_pattern="0 9-17 * * 1-5"
)
```

---

### Pattern 4: Escalating Intervals

Reduce notification frequency for background tasks:

```python
# Critical agent - fast polling
monitor1 = SubAgentMonitor(poll_interval=10)
monitor1.start_monitoring(["critical_agent"])

# Background agent - slow polling
monitor2 = SubAgentMonitor(poll_interval=300)  # 5 minutes
monitor2.start_monitoring(["background_agent"])
```

---

## Error Handling

### Common Issues

**Issue: "APScheduler not available"**
```bash
# Solution: Install APScheduler
pip install apscheduler
```

**Issue: Email notifications failing**
```bash
# Solution: Set environment variables
export NOTIFICATION_EMAIL_USER=your-email@gmail.com
export NOTIFICATION_EMAIL_PASSWORD=app-password
# Note: Use app-specific passwords for Gmail
```

**Issue: Webhook timeouts**
```yaml
# Solution: Increase timeout
notifications:
  webhook:
    timeout: 30  # Increase from default 10
```

**Issue: Storage permissions error**
```bash
# Solution: Ensure directory permissions
mkdir -p monitor_data
chmod 755 monitor_data
```

---

## Security Considerations

### Authentication & Authorization

- ✅ Zero-trust input validation on all agent IDs
- ✅ Secrets loaded from environment variables only
- ✅ No hardcoded credentials in config files
- ✅ Webhook URLs validated before use

### Data Privacy

- ✅ Sensitive data encrypted in transit (HTTPS/TLS)
- ✅ Status history limited by retention policy
- ✅ Alert logs purged after retention period
- ✅ Optional PII redaction in notifications

### Rate Limiting

```yaml
security:
  rate_limiting:
    enabled: true
    max_alerts_per_minute: 10
```

---

## Performance Considerations

### Optimization Tips

1. **Adjust Poll Interval**
   - Production: 30-60 seconds
   - Development: 10-30 seconds
   - Background: 300+ seconds (5+ minutes)

2. **Limit Notification Channels**
   ```python
   # Instead of enabling all channels
   notification_channels=["log", "webhook"]
   # Only enable ones you actually use
   ```

3. **Use Alert Aggregation**
   ```yaml
   aggregation:
     enabled: true
     batch_window: 60
   ```

4. **Configure Retention**
   ```yaml
   polling:
     retention:
       days: 7  # Don't keep forever
       max_history_entries: 1000
   ```

### Monitoring Metrics

Track monitoring performance:

```yaml
performance:
  track_metrics: true
  thresholds:
    slow_poll_threshold: 5  # Alert if polling > 5s
    slow_notification_threshold: 2
```

---

## Testing

### Unit Tests

```python
import pytest
from skills.subagent_monitor_notifier import SubAgentMonitor, AgentStatus

def test_monitor_initialization():
    monitor = SubAgentMonitor(poll_interval=60)
    assert monitor.poll_interval == 60

def test_status_tracking():
    monitor = SubAgentMonitor()
    monitor.start_monitoring(["test_agent"])
    
    status = monitor.get_agent_status("test_agent")
    assert status["agent_id"] == "test_agent"

def test_status_change_detection():
    monitor = SubAgentMonitor()
    monitor.start_monitoring(["test_agent"])
    
    # Simulate status change
    # ... test implementation
    
    history = monitor.get_status_history("test_agent")
    assert len(history) > 0
```

### Integration Tests

```python
# Test with actual OpenClaw framework
from openclaw import Framework

def test_integration_with_openclaw():
    fw = Framework()
    monitor = SubAgentMonitor()
    
    # Create and monitor sub-agent
    agent_id = fw.spawn_subagent("test_skill")
    monitor.start_monitoring([agent_id])
    
    # Verify monitoring works with OpenClaw
    status = monitor.get_agent_status(agent_id)
    assert status["agent_id"] == agent_id
```

---

## Troubleshooting

### Debug Logging

Enable debug logging:

```python
import logging
logging.getLogger("SubAgentMonitor").setLevel(logging.DEBUG)
```

### Check Monitor Status

```python
# Verify monitor is running
print(f"Polling active: {monitor.polling_active}")
print(f"Scheduler running: {monitor.scheduler.running if monitor.scheduler else False}")

# Check agent statuses
for agent_id in monitor.agent_statuses:
    status = monitor.get_agent_status(agent_id)
    print(f"{agent_id}: {status['current_status']}")
```

### View Logs

```bash
# Check monitoring logs
tail -f ./monitor_data/monitor.log

# Check alerts
tail -f ./monitor_data/alerts.log
```

---

## API Reference

### SubAgentMonitor Class

#### Constructor
```python
SubAgentMonitor(
    poll_interval: int = 60,
    retention_days: int = 7,
    notification_channels: List[str] = None,
    enable_scheduling: bool = True
)
```

#### Methods

##### start_monitoring()
```python
start_monitoring(
    agent_ids: List[str],
    schedule_pattern: Optional[str] = None
) -> Dict[str, Any]
```

##### stop_monitoring()
```python
stop_monitoring(agent_id: Optional[str] = None) -> Dict[str, Any]
```

##### get_agent_status()
```python
get_agent_status(agent_id: str) -> Dict[str, Any]
```

##### get_status_history()
```python
get_status_history(
    agent_id: str,
    limit: int = 100
) -> List[Dict[str, Any]]
```

##### execute_skill()
```python
execute_skill(input_data: Dict[str, Any]) -> Dict[str, Any]
```

---

## Contributing

To extend the skill with new features:

1. **Add new notification channels**: Implement `_notify_<channel_name>()` methods
2. **Add new agent sources**: Implement `_fetch_agent_status_from_<source>()` methods
3. **Add new aggregation logic**: Extend aggregation configuration
4. **Add data persistence**: Implement database storage backends

---

## Support & Resources

- **Documentation**: See [README.md](../README.md)
- **Issues**: Report issues in the OpenClaw repository
- **Community**: Join OpenClaw Discord for support

---

## License

MIT License - See LICENSE file for details

---

**Last Updated:** 2024-01-15  
**Maintainer:** OpenClaw Team
