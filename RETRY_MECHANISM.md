# FoodFlow Retry Mechanism

## Overview

The FoodFlow scheduler now implements a robust retry mechanism to prevent endless loops of sync failures. This system automatically disables problematic sync combinations after repeated failures and requires manual intervention to re-enable them.

## Key Features

### 1. Failure Tracking
- **Maximum Retries**: 3 consecutive failures per restaurant/platform combination
- **Automatic Disabling**: Syncs are disabled after exceeding the retry limit
- **Granular Control**: Each restaurant/platform combination is tracked separately

### 2. Logging with Timestamps
- All log messages now include datetime stamps: `[YYYY-MM-DD HH:MM:SS]`
- Clear progression tracking: `(attempt 1/3)`, `(attempt 2/3)`, `(attempt 3/3)`
- Final warning when sync is disabled

### 3. Automatic Recovery
- **Success Reset**: Successful syncs reset failure counts to zero
- **Re-enabling**: Previously disabled syncs are automatically re-enabled on success
- **Cross-sync Recovery**: Daily and weekly syncs can recover hourly sync failures

## How It Works

### Failure Progression
```
Attempt 1: [2024-01-15 14:00:00] WARNING - Availability sync failed for Le Bouzou on uber_eats (attempt 1/3): Authentication failed
Attempt 2: [2024-01-15 15:00:00] WARNING - Availability sync failed for Le Bouzou on uber_eats (attempt 2/3): Authentication failed  
Attempt 3: [2024-01-15 16:00:00] WARNING - Availability sync failed for Le Bouzou on uber_eats (attempt 3/3): Authentication failed
Disabled:  [2024-01-15 17:00:00] ERROR - Disabling automatic sync for Le Bouzou on uber_eats after 3 failures. Manual intervention required.
```

### Recovery Process
```
Manual:    [2024-01-15 18:30:00] INFO - Manual sync triggered for restaurant 1 on uber_eats
Success:   [2024-01-15 18:30:15] INFO - Re-enabled automatic sync for Le Bouzou on uber_eats after successful manual sync
```

## API Endpoints

### Check Scheduler Status
```bash
GET /scheduler/status
```
Returns:
- Current scheduler state
- Failure counts per restaurant/platform
- List of disabled sync combinations
- Maximum retry limit

### Reset Sync Failures
```bash
POST /scheduler/reset-failures
POST /scheduler/reset-failures?restaurant_id=1
POST /scheduler/reset-failures?restaurant_id=1&platform=uber_eats
```
- Reset all failures (no parameters)
- Reset failures for specific restaurant
- Reset failures for specific restaurant/platform combination

### Manual Sync (Auto Re-enables)
```bash
POST /sync/manual
```
- Automatically re-enables disabled syncs when triggered manually
- Resets failure counts on successful manual sync

## Web Interface

### Main Dashboard
- **Scheduler Status** button: View current failure counts and disabled syncs
- **Reset Failures** button: Clear all failure counts and re-enable syncs
- Real-time status indicators

### Status Information
- Number of disabled sync combinations
- Detailed failure counts
- Last sync timestamps
- Error messages for failed syncs

## Configuration

### Retry Settings
```python
class SyncScheduler:
    def __init__(self):
        self.max_retries = 3  # Maximum consecutive failures
        self.failure_counts = {}  # Track failures per sync combination
        self.disabled_syncs = set()  # Disabled sync combinations
```

### Customization
- `max_retries`: Change the number of allowed consecutive failures
- Failure tracking is persistent during scheduler runtime
- Manual intervention always re-enables disabled syncs

## Benefits

### 1. Prevents Endless Loops
- No more infinite failure messages in logs
- System resources are preserved
- Log files remain manageable

### 2. Intelligent Recovery
- Automatic re-enabling on success
- Cross-sync type recovery (daily sync can fix hourly failures)
- Manual override capability

### 3. Operational Visibility
- Clear failure progression tracking
- Dashboard integration for monitoring
- API endpoints for automation

### 4. Graceful Degradation
- Failed platforms don't affect working ones
- Partial sync capability maintained
- System continues operating with reduced functionality

## Monitoring

### Log Messages to Watch
- `WARNING - Availability sync failed for ... (attempt X/3)`
- `ERROR - Disabling automatic sync for ... after 3 failures`
- `INFO - Re-enabled automatic sync for ... after successful sync`

### Dashboard Indicators
- Scheduler Status shows disabled syncs
- Quick action buttons for management
- Real-time failure count display

## Best Practices

### 1. Regular Monitoring
- Check scheduler status daily
- Monitor failure patterns
- Address root causes promptly

### 2. Proactive Management
- Fix authentication issues quickly
- Update API credentials before expiration
- Test manual syncs after configuration changes

### 3. Recovery Procedures
- Use manual sync to test fixes
- Reset failures after resolving issues
- Monitor logs after re-enabling syncs

## Troubleshooting

### Common Scenarios

**Authentication Failures**
1. Check API credentials in configuration
2. Verify platform account status
3. Test manual sync after fixing credentials

**Network Issues**
1. Check internet connectivity
2. Verify platform API endpoints
3. Review firewall settings

**Rate Limiting**
1. Check platform API limits
2. Adjust sync frequency if needed
3. Implement backoff strategies

### Recovery Steps
1. Identify root cause from error messages
2. Fix underlying issue (credentials, network, etc.)
3. Use manual sync to test fix
4. Monitor logs for successful recovery
5. Reset failures if needed

This retry mechanism ensures FoodFlow operates reliably while providing clear visibility into sync issues and recovery processes.