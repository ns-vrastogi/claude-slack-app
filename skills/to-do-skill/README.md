# To-Do Task & Ticket Management Skill

A comprehensive work item tracking system integrated with Claude Code for managing tasks, bugs, QA tickets, incidents, feature requests, and technical debt.

## Quick Start

### Adding Items

**Tasks:**
- "Add task to to-do"
- "Create a new task"

**Bugs:**
- "Add bug"
- "Create bug ticket"
- "Log a bug"

**QA Tickets:**
- "Add QA ticket"
- "Create QA ticket"
- "Log test case"

**Incidents:**
- "Add incident"
- "Log incident"
- "Create incident ticket"

**Feature Requests:**
- "Add feature request"
- "Create feature request"

### Viewing Items

**Daily Overview:**
- "What's up for today?" - Shows all pending and ongoing items
- "Show my tasks" - Shows all work items
- "Show completed tasks" - Shows finished work

**By Type:**
- "Show all bugs" - Lists all bugs
- "Show QA tickets" - Lists all QA test tickets
- "Show incidents" - Lists all incidents
- "Show critical bugs" - Shows high-severity bugs only
- "Show P1 incidents" - Shows P1 incidents only

### Managing Items

- "Mark [item-id] as ongoing" - Start working on an item
- "Mark [item-id] as completed" - Finish an item
- "Mark [item-id] as resolved" - Resolve a bug/incident
- "Update [item-id]" - Modify item details
- "Delete [item-id]" - Remove an item
- "Link [item-id] to [item-id]" - Link related items
- "Add notes to [item-id]" - Add notes to an item

### Statistics & Reporting

- "Show stats" - View comprehensive statistics
- "Show item summary" - Summary of all work items
- "Give me statistics" - Detailed metrics and trends

## Features

### Item Types
- ✅ **Tasks**: General work items and to-dos
- 🐛 **Bugs**: Software bugs and defects
- 🧪 **QA Tickets**: Test cases and QA validation
- 🚨 **Incidents**: Production incidents and outages
- 💡 **Feature Requests**: New feature proposals
- 🔧 **Tech Debt**: Technical debt items

### Status Tracking
- 📌 **Pending**: Not yet started
- 🔄 **Ongoing**: Currently in progress
- ✓ **Completed**: Finished successfully
- ✔️ **Resolved**: Fixed/resolved (bugs, incidents)
- 🔒 **Closed**: Closed after verification

### Priority/Severity Levels
- 🔴 **Critical/P1**: Urgent production issues, critical bugs
- 🟠 **High/P2**: Important work, high-severity issues
- 🟡 **Medium/P3**: Regular work, medium-priority items
- 🟢 **Low/P4**: Nice-to-have improvements, cleanup

### Automatic Tracking
- **Timestamps**: Created, started, completed, resolved dates
- **Duration**: Automatically calculated work duration
- **Related Items**: Link bugs to incidents, QA tickets to bugs
- **Statistics**: Track completion rates, trends, averages

## Item-Specific Features

### Bugs 🐛
- **Severity**: Critical, High, Medium, Low
- **Environment**: Production, Staging, Development
- **Reproducibility**: Yes/No tracking
- **Reproduction Steps**: Detailed steps to reproduce
- **Affected Version**: Build/version where bug was found
- **Found By**: QA, Customer, or Internal
- **Related Tickets**: Link to incidents, QA tickets, tasks

### QA Tickets 🧪
- **Test Case ID**: Link to test case documentation
- **Test Type**: Functional, Performance, Regression, Integration
- **Build Version**: Version under test
- **Test Environment**: Staging, QA, Production
- **Pass/Fail Status**: Test result tracking
- **Related Bugs**: Link to bugs found during testing

### Incidents 🚨
- **Severity**: P1, P2, P3, P4
- **Impact**: Critical, High, Medium, Low
- **Affected Services**: Which services are impacted
- **Customer Facing**: Yes/No tracking
- **Root Cause**: Root cause analysis
- **Mitigation**: Steps taken to mitigate
- **Postmortem Required**: Flag for postmortem requirement
- **Related Tickets**: Link to bugs and tasks

### Feature Requests 💡
- **Requested By**: Customer, Internal, PM
- **Business Value**: High, Medium, Low
- **Implementation Complexity**: High, Medium, Low
- **Target Version**: Planned release version
- **Related Tasks**: Link to implementation tasks

## Data Storage

All items are stored in:
```
~/.claude/skills/to-do-skill/tasks.json
```

Storage format: JSON (version 2.0)
- Supports all item types
- Maintains bidirectional links between related items
- Tracks comprehensive statistics
- Human-readable for manual editing if needed

## Common Workflows

### Starting Your Day
```
You: What's up for today?
Claude: 📋 Work Items for Today
        🚨 1 P1 incident ongoing
        🐛 3 bugs (1 critical, 2 high)
        ✅ 5 tasks (2 ongoing, 3 pending)
        🧪 2 QA tickets
```

### Logging a Production Bug
```
You: Add bug
Claude: What's the bug?
You: VPP gateway crashes when handling 10k+ tunnels
Claude: What severity?
You: Critical
Claude: What environment?
You: Production
Claude: Is it reproducible?
You: Yes
Claude: 🐛 Bug logged!
        ID: bug-1706024500-x7k
        Severity: Critical | Environment: Production
```

### Handling an Incident
```
You: Add incident
Claude: What's the incident?
You: ECGW service down in IAD datacenter
Claude: What severity?
You: P1
Claude: 🚨 Incident logged!
        ID: incident-1706024600-r5n
        Severity: P1 | Status: Ongoing

[After resolution]
You: Mark incident-1706024600-r5n as resolved
Claude: ✓ Incident resolved!
        Duration: 2 hours 15 minutes
```

### Running QA Tests
```
You: Add QA ticket
Claude: What are you testing?
You: IPSEC tunnel failover behavior
Claude: Test case ID?
You: TC-5678
Claude: 🧪 QA Ticket created!
        ID: qa-1706024700-m2p

[After testing]
You: Mark qa-1706024700-m2p as completed
Claude: What was the result?
You: Fail
Claude: ✓ Test completed | Result: Fail

You: Add bug
Claude: [Creates bug for failed test]
You: Link bug-1706024800-k3m to qa-1706024700-m2p
Claude: ✓ Items linked successfully!
```

### Linking Related Items
```
You: Link bug-456 to incident-123
Claude: ✓ Items linked successfully!
        🐛 bug-456: VPP gateway crashes
          ↔️ linked to
        🚨 incident-123: ECGW service down
```

### End of Day Review
```
You: Show completed tasks
Claude: ✅ Completed Today (5 items):
        - 3 tasks completed
        - 1 bug resolved
        - 1 QA test passed

You: Show stats
Claude: 📊 This week: 15 created, 12 completed
        Bug fix rate: 2.5 days average
        ⚠️ 3 items pending for 7+ days
```

## Item Metadata Tracked

**Common to All Items:**
- Created Date, Started Date, Completed Date
- Duration (automatically calculated)
- Priority/Severity level
- Status (pending/ongoing/completed/resolved/closed)
- Category and Tags
- Notes and additional context
- Related items (bidirectional links)

**Type-Specific:**
- Bug: Severity, Environment, Reproducibility, Affected Version
- QA: Test Case ID, Test Type, Build Version, Pass/Fail
- Incident: P-level, Impact, Affected Services, Customer Facing
- Feature: Business Value, Complexity, Target Version

## Tips

1. **Use the right item type** - Bugs, QA tickets, and incidents have specific tracking fields
2. **Link related items** - Connect bugs to incidents, QA tests to bugs for traceability
3. **Set proper severity** - Use Critical/P1 for urgent issues requiring immediate attention
4. **Track time** - Mark items as "ongoing" when you start to track work duration
5. **Review regularly** - Use "what's up for today" daily, "show stats" weekly
6. **Add notes** - Capture important context, root causes, and learnings
7. **Close the loop** - Mark bugs as resolved, incidents as closed after verification

## Advanced Features

- **Fuzzy Matching**: Reference items by partial ID or title
- **Type-Specific Views**: Filter by item type, severity, or status
- **Statistics & Trends**: Track completion rates, identify bottlenecks
- **Alerts**: Get notified about critical bugs, long-pending items
- **Bidirectional Linking**: Automatically maintain relationships between items
- **Duration Tracking**: Automatic calculation of work time
- **Rich Formatting**: Emoji icons, color-coded priorities, structured output

## For More Details

See **SKILL.md** for complete documentation including:
- Detailed command reference for all item types
- Complete data structure specifications
- Error handling procedures
- All workflow examples
- Implementation guidelines
- Testing checklist
- File operations and storage format
