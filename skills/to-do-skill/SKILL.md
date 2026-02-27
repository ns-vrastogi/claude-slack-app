# To-Do Task Management Skill

## Skill Metadata
- **Name**: `to-do-skill`
- **Description**: Personal task management system for tracking work items with priorities, statuses, and metadata
- **Version**: 1.0.0
- **Storage**: `tasks.json` (in skill directory)

## Overview
This skill provides a comprehensive task and ticket management system that allows you to:
- Create and organize tasks, bugs, QA tickets, incidents, and feature requests
- Track item status (pending, ongoing, completed, resolved, closed)
- View daily task and ticket lists
- Monitor item lifecycle with timestamps
- Filter and search by type, priority, severity, and status
- Add notes and context to items
- Track bug severity and QA test cases
- Link related tickets and tasks

## Activation Patterns

The skill should automatically activate when the user says phrases like:
- "add task to to-do" or "add a task"
- "add bug" or "create bug ticket"
- "add QA ticket" or "create QA ticket"
- "add incident" or "log incident"
- "add feature request"
- "what's up for today" or "show today's tasks"
- "show my tasks" or "list my tasks"
- "show all bugs" or "list bugs"
- "show QA tickets" or "list QA tickets"
- "show high severity bugs"
- "mark [item-id] as [completed/ongoing/pending/resolved/closed]"
- "update [item-id]"
- "delete [item-id]"
- "show completed tasks" or "show pending tasks"
- "set priority for [item-id]"
- "what am I working on" or "current tasks"
- "show critical bugs" or "show P1 bugs"

## Data Structure

### Item Types

The system supports multiple item types:
- **task**: General work items, to-dos
- **bug**: Software bugs and defects
- **qa_ticket**: QA testing tickets
- **incident**: Production incidents or outages
- **feature_request**: New feature requests
- **tech_debt**: Technical debt items

### Base Item Object

All items share these common fields:
```json
{
  "id": "unique-item-id",
  "type": "task|bug|qa_ticket|incident|feature_request|tech_debt",
  "title": "Item title/description",
  "status": "pending|ongoing|completed|resolved|closed",
  "priority": "critical|high|medium|low",
  "created_at": "2026-01-23T15:30:00Z",
  "started_at": "2026-01-23T16:00:00Z",
  "completed_at": null,
  "resolved_at": null,
  "closed_at": null,
  "notes": "Additional context or notes",
  "tags": ["work", "ipsec", "testing"],
  "estimated_hours": 4,
  "category": "development|testing|deployment|debugging|other"
}
```

### Bug-Specific Fields
```json
{
  "type": "bug",
  "severity": "critical|high|medium|low",
  "reproducible": true,
  "environment": "production|staging|development",
  "affected_version": "134.0.0.3391",
  "found_by": "QA|Customer|Internal",
  "reproduction_steps": "Steps to reproduce the bug",
  "related_tickets": ["qa-123", "incident-456"]
}
```

### QA Ticket-Specific Fields
```json
{
  "type": "qa_ticket",
  "test_case_id": "TC-1234",
  "test_type": "functional|performance|regression|integration",
  "build_version": "134.0.0.3391",
  "test_environment": "staging|qa|production",
  "pass_fail": "pass|fail|blocked|skipped",
  "related_bugs": ["bug-789"]
}
```

### Incident-Specific Fields
```json
{
  "type": "incident",
  "severity": "p1|p2|p3|p4",
  "impact": "critical|high|medium|low",
  "affected_services": ["ipsec-gateway", "vpn"],
  "customer_facing": true,
  "root_cause": "Description of root cause",
  "mitigation": "Steps taken to mitigate",
  "postmortem_required": true,
  "related_tickets": ["bug-123", "task-456"]
}
```

### Feature Request-Specific Fields
```json
{
  "type": "feature_request",
  "requested_by": "Customer|Internal|PM",
  "business_value": "high|medium|low",
  "implementation_complexity": "high|medium|low",
  "target_version": "135.0.0",
  "related_tasks": ["task-789"]
}
```

### Storage File Format (tasks.json)
```json
{
  "version": "2.0",
  "last_updated": "2026-01-23T15:30:00Z",
  "items": [
    { /* item object */ },
    { /* item object */ }
  ],
  "statistics": {
    "total_tasks": 10,
    "total_bugs": 5,
    "total_qa_tickets": 3,
    "total_incidents": 2
  }
}
```

## Commands and Operations

### 1. Add Task
**Trigger**: "add task to to-do", "create new task"

**Required Information**:
- Task title/description
- Priority (default: medium)
- Category (optional)
- Estimated hours (optional)
- Tags (optional)

**Process**:
1. Read existing tasks.json (or create if doesn't exist)
2. Generate unique ID: `task-{timestamp}-{random}`
3. Create task object with type="task", status="pending"
4. Set created_at to current timestamp
5. Add to items array
6. Save tasks.json
7. Confirm to user with task ID and summary

**Example**:
```
User: Add task to to-do
Assistant: I'll help you add a new task. What's the task?
User: Complete performance testing for IPSEC gateway
Assistant: Got it. What priority? (critical/high/medium/low)
User: High
Assistant: [Creates task and confirms]
✓ Task added successfully!
ID: task-1706024400-a3f
Title: Complete performance testing for IPSEC gateway
Type: Task
Priority: High
Status: Pending
Created: 2026-01-23 15:30:00
```

### 2. Add Bug
**Trigger**: "add bug", "create bug ticket", "log a bug"

**Required Information**:
- Bug title/description
- Severity (critical/high/medium/low)
- Environment (production/staging/development)
- Reproducible (yes/no)
- Reproduction steps (optional)
- Affected version (optional)
- Found by (QA/Customer/Internal)

**Process**:
1. Read existing tasks.json
2. Generate unique ID: `bug-{timestamp}-{random}`
3. Create bug object with type="bug", status="pending"
4. Collect bug-specific fields
5. Set created_at to current timestamp
6. Add to items array
7. Save tasks.json
8. Confirm to user with bug ID and summary

**Example**:
```
User: Add bug
Assistant: What's the bug?
User: VPP gateway crashes when handling 10k+ tunnels
Assistant: What severity? (critical/high/medium/low)
User: Critical
Assistant: What environment? (production/staging/development)
User: Production
Assistant: Is it reproducible? (yes/no)
User: Yes
Assistant: [Creates bug and confirms]
🐛 Bug logged successfully!
ID: bug-1706024500-x7k
Title: VPP gateway crashes when handling 10k+ tunnels
Type: Bug
Severity: Critical
Status: Pending
Environment: Production
Reproducible: Yes
Created: 2026-01-23 15:35:00
```

### 3. Add QA Ticket
**Trigger**: "add QA ticket", "create QA ticket", "log test case"

**Required Information**:
- Test description
- Test case ID (optional)
- Test type (functional/performance/regression/integration)
- Build version
- Test environment
- Pass/Fail status (optional, defaults to pending)

**Process**:
1. Read existing tasks.json
2. Generate unique ID: `qa-{timestamp}-{random}`
3. Create QA ticket object with type="qa_ticket"
4. Collect QA-specific fields
5. Set created_at to current timestamp
6. Add to items array
7. Save tasks.json
8. Confirm to user with QA ticket ID

**Example**:
```
User: Add QA ticket
Assistant: What are you testing?
User: IPSEC tunnel failover behavior
Assistant: Test case ID? (or press enter to skip)
User: TC-5678
Assistant: Test type? (functional/performance/regression/integration)
User: Functional
Assistant: Build version?
User: 134.0.0.3391
Assistant: [Creates QA ticket and confirms]
✓ QA Ticket created!
ID: qa-1706024600-m2p
Title: IPSEC tunnel failover behavior
Type: QA Ticket
Test Case: TC-5678
Test Type: Functional
Build: 134.0.0.3391
Status: Pending
Created: 2026-01-23 15:40:00
```

### 4. Add Incident
**Trigger**: "add incident", "log incident", "create incident ticket"

**Required Information**:
- Incident description
- Severity (p1/p2/p3/p4)
- Impact (critical/high/medium/low)
- Affected services
- Customer facing (yes/no)
- Mitigation steps (optional)

**Process**:
1. Read existing tasks.json
2. Generate unique ID: `incident-{timestamp}-{random}`
3. Create incident object with type="incident", status="ongoing"
4. Collect incident-specific fields
5. Set created_at and started_at to current timestamp
6. Add to items array
7. Save tasks.json
8. Confirm to user with incident ID

**Example**:
```
User: Add incident
Assistant: What's the incident?
User: ECGW service down in IAD datacenter
Assistant: What severity? (p1/p2/p3/p4)
User: P1
Assistant: What's the impact? (critical/high/medium/low)
User: Critical
Assistant: Which services are affected?
User: ECGW, IPSEC tunnels
Assistant: Is this customer facing? (yes/no)
User: Yes
Assistant: [Creates incident and confirms]
🚨 Incident logged!
ID: incident-1706024700-r5n
Title: ECGW service down in IAD datacenter
Type: Incident
Severity: P1
Impact: Critical
Affected Services: ECGW, IPSEC tunnels
Customer Facing: Yes
Status: Ongoing
Created: 2026-01-23 15:45:00
```

### 5. Add Feature Request
**Trigger**: "add feature request", "create feature request"

**Required Information**:
- Feature description
- Requested by (Customer/Internal/PM)
- Business value (high/medium/low)
- Implementation complexity (optional)
- Target version (optional)

**Process**:
1. Read existing tasks.json
2. Generate unique ID: `feature-{timestamp}-{random}`
3. Create feature request object with type="feature_request", status="pending"
4. Collect feature-specific fields
5. Set created_at to current timestamp
6. Add to items array
7. Save tasks.json

**Example**:
```
User: Add feature request
Assistant: What's the feature?
User: Add support for IPSec over QUIC protocol
Assistant: Who requested this? (Customer/Internal/PM)
User: Customer
Assistant: Business value? (high/medium/low)
User: High
Assistant: [Creates feature request and confirms]
💡 Feature request created!
ID: feature-1706024800-k9w
Title: Add support for IPSec over QUIC protocol
Type: Feature Request
Requested By: Customer
Business Value: High
Status: Pending
Created: 2026-01-23 15:50:00
```

### 6. List Today's Items
**Trigger**: "what's up for today", "show today's items", "daily summary"

**Process**:
1. Read tasks.json
2. First show completed items (all types) sorted by completion time
3. Then show ongoing items (all types) sorted by priority/severity
4. Finally show pending items (all types) sorted by priority/severity
5. Display with relevant metadata and visual enhancements

**Output Format**:
```
📋 Work Items for Today (2026-01-23)

═══════════════════════════════════════════════════════════
🎉 COMPLETED ITEMS (2)
═══════════════════════════════════════════════════════════

  ✓ task-002: Perform VPP GRE scale & performance testing for build 134
    Priority: High | Completed: Today at 19:40
    Category: testing | Tags: vpp, gre, scale, performance
    Duration: N/A
    🎯 Great work!

  ✓ qa-005: Verify tunnel failover behavior
    Test Case: TC-1234 | Result: Pass
    Completed: Today at 14:30
    Build: 134.0.0.3391
    💯 Test passed!

═══════════════════════════════════════════════════════════
🔥 ONGOING ITEMS (2)
═══════════════════════════════════════════════════════════

🚨 INCIDENTS
  [ongoing] incident-001: ECGW service down in IAD datacenter
    Severity: P1 | Started: 2 hours ago
    Customer Facing: Yes | Affected: ECGW, IPSEC tunnels
    ⚡ URGENT - Needs immediate attention!

🐛 BUGS
  [ongoing] bug-005: Memory leak in GRE tunnel handler
    Severity: High | Started: 3 days ago
    Environment: Staging | Reproducible: Yes
    🔍 In progress

═══════════════════════════════════════════════════════════
📌 PENDING ITEMS - NEED YOUR ATTENTION! (5)
═══════════════════════════════════════════════════════════

🚨 INCIDENTS (1)
  ⚠️  [pending] incident-003: Performance degradation in IAD
    Severity: P2 | Created: 3 hours ago
    Customer Facing: No | Affected: VPP gateways
    👉 Scheduled: Today

🐛 BUGS (1)
  ⚠️  [pending] bug-002: VPP gateway crashes with 10k+ tunnels
    Severity: Critical | Created: 1 day ago
    Environment: Production | Reproducible: Yes
    👉 Needs investigation

✅ TASKS (3)
  🔴 HIGH PRIORITY
    ⚠️  [pending] task-001: Work on scale performance testing via real proxy and CFW
      Created: 4 days ago | Scheduled: Wednesday
      Category: testing | Tags: performance, proxy, cfw
      👉 Focus on scale performance testing using real proxy and CFW infrastructure

    ⚠️  [pending] task-004: Test s&p and padding issue on latest 134 version
      Created: 10 minutes ago | Scheduled: Wednesday
      Category: testing | Tags: scale, performance, padding
      👉 Test scale & performance (s&p) and padding issue on build 134

  🟡 MEDIUM PRIORITY
    ⚠️  [pending] task-007: Update documentation for GRE tunnels
      Created: 1 day ago | Scheduled: Friday
      Category: documentation
      👉 Documentation update needed

═══════════════════════════════════════════════════════════
📊 SUMMARY
═══════════════════════════════════════════════════════════
Total: 9 items
  ✅ Completed: 2 items (2 today!)
  🔄 Ongoing: 2 items (1 P1 incident, 1 high bug)
  📌 Pending: 5 items (1 incident, 1 critical bug, 3 tasks)

🎯 Next Action: Focus on pending P1 incident and critical bugs first!
```

### 7. Show All Bugs
**Trigger**: "show all bugs", "list bugs", "show bug list"

**Process**:
1. Read tasks.json
2. Filter items where type="bug"
3. Sort by severity (critical → high → medium → low)
4. Group by status
5. Display with bug-specific details

**Output Format**:
```
🐛 Bug List

🔥 CRITICAL SEVERITY
  [ongoing] bug-123: VPP gateway crashes with 10k+ tunnels
    Status: Ongoing | Started: 1 day ago
    Environment: Production | Reproducible: Yes
    Found By: Customer
    Related: incident-456

⚠️ HIGH SEVERITY
  [pending] bug-456: Memory leak in GRE tunnel handler
    Status: Pending | Created: 3 days ago
    Environment: Staging | Reproducible: Yes
    Found By: QA | Affected Version: 134.0.0.3391

  [resolved] bug-789: ECGW performance degradation
    Status: Resolved | Completed: 2 days ago
    Duration: 5 days
    Environment: Production

Summary: 3 bugs (1 ongoing, 1 pending, 1 resolved)
```

### 8. Show QA Tickets
**Trigger**: "show QA tickets", "list QA tickets", "show test cases"

**Process**:
1. Read tasks.json
2. Filter items where type="qa_ticket"
3. Group by test_type
4. Display with QA-specific details

**Output Format**:
```
🧪 QA Tickets

📊 PERFORMANCE TESTING
  [ongoing] qa-123: Load test VPP gateway with 50k tunnels
    Test Case: TC-9001 | Build: 134.0.0.3391
    Started: 2 hours ago | Environment: QA

⚙️ FUNCTIONAL TESTING
  [pending] qa-456: Test IPSEC tunnel failover
    Test Case: TC-5678 | Build: 134.0.0.3391
    Created: 4 hours ago | Environment: Staging

  [completed] qa-789: Verify GRE tunnel configuration
    Test Case: TC-3456 | Build: 134.0.0.3390
    Result: Pass | Completed: 1 day ago

🔄 REGRESSION TESTING
  [pending] qa-234: Regression suite for ECGW
    Build: 134.0.0.3391 | Created: 1 day ago

Summary: 4 QA tickets (1 ongoing, 2 pending, 1 completed)
  Pass: 1 | Fail: 0 | Pending: 3
```

### 9. Show Incidents
**Trigger**: "show incidents", "list incidents", "show active incidents"

**Process**:
1. Read tasks.json
2. Filter items where type="incident"
3. Sort by severity (p1 → p2 → p3 → p4)
4. Display with incident-specific details

**Output Format**:
```
🚨 Incidents

🔴 P1 - CRITICAL
  [ongoing] incident-123: ECGW service down in IAD datacenter
    Impact: Critical | Started: 2 hours ago
    Customer Facing: Yes
    Affected Services: ECGW, IPSEC tunnels
    Mitigation: Failover to backup datacenter
    Related: bug-456, task-789

🟡 P2 - HIGH
  [resolved] incident-456: VPP memory exhaustion
    Impact: High | Resolved: 1 day ago
    Duration: 3 hours
    Customer Facing: No
    Root Cause: Memory leak in tunnel cleanup
    Postmortem: Required

Summary: 2 incidents (1 ongoing P1, 1 resolved P2)
```

### 10. Show Critical/High Severity Items
**Trigger**: "show critical bugs", "show P1 incidents", "show high priority items"

**Process**:
1. Read tasks.json
2. Filter by severity/priority (critical or high)
3. Group by type
4. Display sorted by urgency

**Output Format**:
```
⚠️ Critical & High Severity Items

🚨 INCIDENTS
  [ongoing] incident-123: ECGW service down (P1)
    Started: 2 hours ago | Customer Facing: Yes

🐛 BUGS
  [ongoing] bug-456: VPP gateway crashes (Critical)
    Started: 1 day ago | Production | Reproducible: Yes

  [pending] bug-789: Memory leak in GRE handler (High)
    Created: 3 days ago | Staging

✅ TASKS
  [pending] task-234: Fix authentication bypass (High)
    Created: 5 hours ago | Category: security

Summary: 4 critical/high items requiring immediate attention
```

### 3. Update Task Status
**Trigger**: "mark task as [status]", "update task [id]"

**Process**:
1. Identify task by ID or title (fuzzy match)
2. Update status field
3. Update timestamp:
   - If changing to "ongoing": set started_at
   - If changing to "completed": set completed_at
4. Save tasks.json
5. Confirm to user

**Status Transitions**:
- pending → ongoing: Set started_at timestamp
- ongoing → completed: Set completed_at timestamp
- Any → pending: Clear started_at and completed_at
- completed → ongoing: Set started_at, clear completed_at

### 4. Show All Tasks
**Trigger**: "show all tasks", "list my tasks"

**Process**:
1. Read tasks.json
2. Group by status (ongoing → pending → completed)
3. Sort by priority within each group
4. Display with full details

### 5. Show Completed Tasks
**Trigger**: "show completed tasks", "what did I finish"

**Process**:
1. Filter tasks where status="completed"
2. Sort by completed_at (most recent first)
3. Show completion date and duration

**Output Format**:
```
✅ Completed Tasks

✓ task-003: Setup ECGW monitoring
  Priority: High
  Completed: 2026-01-22 (1 day ago)
  Duration: 2 days (started 2026-01-20)

✓ task-005: Fix VPP memory leak
  Priority: High
  Completed: 2026-01-20 (3 days ago)
  Duration: 5 days (started 2026-01-15)

Total: 2 completed tasks
```

### 6. Delete Task
**Trigger**: "delete task [id/title]", "remove task"

**Process**:
1. Identify task by ID or title
2. Confirm with user (show task details)
3. Remove from tasks array
4. Save tasks.json
5. Confirm deletion

### 7. Update Task Details
**Trigger**: "update task [id]", "change priority", "add notes to task"

**Operations**:
- Change priority
- Add/update notes
- Add/remove tags
- Update title
- Change category
- Update estimated hours

### 8. Search Tasks
**Trigger**: "find task about [keyword]", "search tasks"

**Process**:
1. Search in title, notes, and tags
2. Return matching tasks with context
3. Highlight matching terms

### 11. Link Related Items
**Trigger**: "link [item-id] to [item-id]", "add related ticket"

**Process**:
1. Read tasks.json
2. Find both items by ID
3. Add to related_tickets/related_bugs/related_tasks array
4. Update both items (bidirectional link)
5. Save tasks.json
6. Confirm linkage

**Example**:
```
User: Link bug-123 to incident-456
Assistant: [Links the items]
✓ Items linked successfully!
🐛 bug-123: VPP gateway crashes
  ↔️ linked to
🚨 incident-456: ECGW service down

Both items have been updated with the relationship.
```

### 12. Update Item Details
**Trigger**: "update [item-id]", "change priority", "add notes to [item-id]"

**Operations**:
- Change priority/severity
- Add/update notes
- Add/remove tags
- Update title
- Change category
- Update estimated hours
- Update item-specific fields (environment, test_case_id, etc.)

### 13. Item Statistics
**Trigger**: "show stats", "show item summary", "give me statistics"

**Output**:
```
📊 Work Item Statistics

BY TYPE:
  ✅ Tasks: 15 (5 ongoing, 7 pending, 3 completed)
  🐛 Bugs: 8 (2 ongoing, 3 pending, 3 resolved)
  🧪 QA Tickets: 12 (3 ongoing, 5 pending, 4 completed)
  🚨 Incidents: 3 (1 ongoing, 0 pending, 2 resolved)
  💡 Feature Requests: 5 (0 ongoing, 4 pending, 1 completed)

BY PRIORITY/SEVERITY:
  🔴 Critical/P1: 5 items (2 bugs, 1 incident, 2 tasks)
  🟠 High/P2: 8 items
  🟡 Medium/P3: 12 items
  🟢 Low/P4: 10 items

THIS WEEK:
  Created: 12 items (4 tasks, 3 bugs, 3 QA, 2 features)
  Completed: 8 items (5 tasks, 2 bugs, 1 QA)
  Average completion time: 3.2 days

ALERTS:
  ⚠️ 2 critical bugs in production
  ⚠️ 1 P1 incident ongoing for 2+ hours
  ⚠️ 3 tasks pending for 7+ days

TRENDS:
  Bug fix rate: 2.5 days average
  QA test completion: 1.8 days average
  Longest ongoing: bug-456 (14 days)
```

## Helper Functions

### Calculate Duration
For ongoing tasks: current_time - started_at
For completed tasks: completed_at - started_at

### Human-Readable Dates
- "2 hours ago"
- "3 days ago"
- "Started 5 days ago"
- "Completed yesterday"

### Item ID Generation
Format: `{type}-{timestamp}-{random-3-char}`

Examples:
- Task: `task-1706024400-a3f`
- Bug: `bug-1706024500-x7k`
- QA Ticket: `qa-1706024600-m2p`
- Incident: `incident-1706024700-r5n`
- Feature Request: `feature-1706024800-k9w`
- Tech Debt: `debt-1706024900-t4j`

### Item Type Icons

Use these emojis for visual identification:
- ✅ Task
- 🐛 Bug
- 🧪 QA Ticket
- 🚨 Incident
- 💡 Feature Request
- 🔧 Tech Debt

### Status Icons

- 📌 Pending
- 🔄 Ongoing
- ✓ Completed
- ✔️ Resolved
- 🔒 Closed

### Fuzzy Task Matching
When user refers to task by partial title:
1. Try exact ID match first
2. Try case-insensitive title match
3. Try partial title match (contains)
4. If multiple matches, ask user to clarify

## File Operations

### Initialize tasks.json
If file doesn't exist, create with:
```json
{
  "version": "2.0",
  "last_updated": "2026-01-23T15:30:00Z",
  "items": [],
  "statistics": {
    "total_tasks": 0,
    "total_bugs": 0,
    "total_qa_tickets": 0,
    "total_incidents": 0,
    "total_feature_requests": 0,
    "total_tech_debt": 0
  }
}
```

### Read Tasks
```bash
cat ~/.claude/skills/to-do-skill/tasks.json
```

### Write Tasks
- Read entire file
- Parse JSON
- Modify tasks array
- Update last_updated timestamp
- Write back to file (pretty-printed)

## Best Practices

1. **Always backup**: Before any destructive operation, keep the original data
2. **Atomic writes**: Write to temp file, then move to tasks.json
3. **Validation**: Validate JSON structure before writing
4. **Error handling**: Handle missing files, corrupt JSON, etc.
5. **User confirmation**: Confirm before deleting or making major changes
6. **Concise output**: Keep task lists readable, don't overwhelm
7. **Smart defaults**: Use sensible defaults (medium priority, etc.)

## Priority Guidelines

**HIGH** 🔴:
- Urgent production issues
- Time-sensitive tasks
- Blocking items for others

**MEDIUM** 🟡:
- Regular development work
- Scheduled testing
- Documentation

**LOW** 🟢:
- Nice-to-have improvements
- Code cleanup
- Learning/research

## Categories

Suggested categories:
- `development`: Code development
- `testing`: Performance/scale testing
- `deployment`: Deployment operations
- `debugging`: Troubleshooting issues
- `meeting`: Meetings and discussions
- `documentation`: Docs and knowledge sharing
- `research`: Investigation and research
- `review`: Code/design reviews
- `other`: Miscellaneous

## Example Workflows

### Starting Your Day
```
User: What's up for today?
Assistant: [Shows completed items first, then ongoing, then pending with visual enhancements]
📋 Work Items for Today (2026-01-23)

═══════════════════════════════════════════════════════════
🎉 COMPLETED ITEMS (2)
═══════════════════════════════════════════════════════════
  ✓ task-005: Performance testing completed
    🎯 Great work!

═══════════════════════════════════════════════════════════
🔥 ONGOING ITEMS (3)
═══════════════════════════════════════════════════════════
🚨 INCIDENTS (1) - P1 ongoing
🐛 BUGS (2) - 1 critical, 1 high

═══════════════════════════════════════════════════════════
📌 PENDING ITEMS - NEED YOUR ATTENTION! (5)
═══════════════════════════════════════════════════════════
✅ TASKS (3) - 2 high priority, 1 medium
🧪 QA TICKETS (2) - performance testing
  ⚠️  Each pending item shows with attention icon
  👉 Clear action items

User: Mark task-123 as ongoing
Assistant: [Updates task status]
✓ task-123 is now ongoing
```

### Adding a New Task
```
User: Add task to to-do
Assistant: What's the task?
User: Review performance metrics for IPSEC tunnels
Assistant: What priority? (critical/high/medium/low)
User: High
Assistant: [Creates task and confirms with ID]
✓ Task added!
ID: task-1706024400-a3f
```

### Logging a Bug
```
User: Add bug
Assistant: What's the bug?
User: Memory leak in VPP tunnel cleanup
Assistant: What severity? (critical/high/medium/low)
User: High
Assistant: What environment? (production/staging/development)
User: Staging
Assistant: Is it reproducible? (yes/no)
User: Yes
Assistant: [Creates bug and confirms]
🐛 Bug logged!
ID: bug-1706024500-x7k
Severity: High | Environment: Staging

User: Add notes to bug-1706024500-x7k
Assistant: What notes should I add?
User: Memory usage grows by 100MB per hour, affects long-running tunnels
Assistant: ✓ Notes added to bug-1706024500-x7k
```

### Handling an Incident
```
User: Add incident
Assistant: What's the incident?
User: VPP gateway unresponsive in IAD datacenter
Assistant: What severity? (p1/p2/p3/p4)
User: P1
Assistant: What's the impact?
User: Critical
Assistant: Which services are affected?
User: IPSEC, GRE tunnels
Assistant: Is this customer facing?
User: Yes
Assistant: [Creates incident]
🚨 Incident logged!
ID: incident-1706024600-r5n
Severity: P1 | Impact: Critical | Customer Facing: Yes
Status: Ongoing

[Later, after resolution...]
User: Mark incident-1706024600-r5n as resolved
Assistant: ✓ Incident resolved!
Duration: 2 hours 15 minutes
Postmortem required: Yes
```

### Creating and Running QA Tests
```
User: Add QA ticket
Assistant: What are you testing?
User: Load test VPP gateway with 50k IPSEC tunnels
Assistant: Test case ID?
User: TC-9001
Assistant: Test type? (functional/performance/regression/integration)
User: Performance
Assistant: Build version?
User: 134.0.0.3391
Assistant: [Creates QA ticket]
🧪 QA Ticket created!
ID: qa-1706024700-m2p
Test Case: TC-9001 | Build: 134.0.0.3391

User: Mark qa-1706024700-m2p as ongoing
Assistant: ✓ QA test is now ongoing

[After testing...]
User: Mark qa-1706024700-m2p as completed
Assistant: What was the result? (pass/fail/blocked/skipped)
User: Fail
Assistant: ✓ QA test completed
Result: Fail | Duration: 3 hours

User: Add bug
Assistant: What's the bug?
User: Performance degradation at 45k tunnels
Assistant: [Creates bug...]
User: Link bug-1706024800-k3m to qa-1706024700-m2p
Assistant: ✓ Items linked successfully!
```

### Tracking Multiple Related Items
```
User: Show all bugs
Assistant: [Shows bug list]
🐛 Bug List
🔥 CRITICAL: 2 bugs
⚠️ HIGH: 3 bugs
...

User: Show critical bugs
Assistant: [Filters to show only critical bugs]

User: Mark bug-456 as ongoing
Assistant: ✓ bug-456 is now ongoing

User: Link bug-456 to incident-123
Assistant: ✓ Items linked successfully!
🐛 bug-456 ↔️ 🚨 incident-123
```

### End of Day Review
```
User: Show completed tasks
Assistant: [Shows all completed items from today]
✅ Completed Today (5 items):
- 3 tasks
- 1 bug resolved
- 1 QA test passed

User: What's still pending?
Assistant: [Shows ongoing and pending items]
📋 Ongoing & Pending (8 items):
- 1 P1 incident (ongoing for 4 hours)
- 2 high severity bugs
- 5 tasks

User: Show stats
Assistant: [Shows comprehensive statistics]
```

### Weekly Review
```
User: Show stats
Assistant: [Shows statistics including weekly trends]
📊 This week: 15 items created, 12 completed
Bug fix rate: 2.5 days average
3 items pending for 7+ days - need attention!
```

## Error Handling

### Missing tasks.json
- Create new file with empty tasks array
- Inform user this is their first task

### Corrupt JSON
- Show error message
- Ask if user wants to reset (backup old file)
- Provide recovery options

### Task Not Found
- Show similar tasks (fuzzy match)
- Ask user to clarify
- Suggest using task ID for precision

### Duplicate Detection
- When adding task, check for similar titles
- Warn if found
- Allow user to proceed or cancel

## Storage Location

**Primary Storage**: `~/.claude/skills/to-do-skill/tasks.json`

**Backup Strategy** (optional):
- Keep `.tasks.json.backup` before destructive operations
- Automatic backup before bulk operations

## Integration with CLAUDE.md

This skill can reference the user's role and responsibilities from CLAUDE.md:
- Suggest task categories based on user's work (IPSEC/GRE, testing)
- Tag tasks with relevant technologies (VPP, ECGW)
- Link tasks to common workflows

## Future Enhancements

Potential additions:
- Task dependencies (blocked by other tasks)
- Recurring tasks
- Task templates for common workflows
- Time tracking (actual vs estimated)
- Export to other formats (markdown, CSV)
- Integration with calendar
- Subtasks/checklist items
- Task reminders
- Weekly/monthly reports

## Implementation Notes

When implementing this skill, Claude should:
1. **Always read tasks.json first** before any operation
2. **Use clear, concise output** with emojis for visual clarity
3. **Show completed items FIRST** to celebrate achievements, then ongoing, then pending
4. **Use visual separators** (═══) to clearly separate sections
5. **Add attention icons** (⚠️ 👉) to pending items to draw focus
6. **Confirm destructive operations** (delete, bulk updates)
7. **Handle edge cases gracefully** (empty task list, missing fields)
8. **Provide helpful suggestions** (next task to work on, overdue items)
9. **Be conversational** but efficient
10. **Auto-save** after every operation
11. **Show relevant context** (how long task has been pending/ongoing)
12. **Celebrate completions** with encouraging messages (🎯 Great work! 💯 Well done!)

## Testing Checklist

Before deploying this skill:

**Item Creation:**
- [ ] Create task with all fields
- [ ] Create bug with all bug-specific fields
- [ ] Create QA ticket with test case details
- [ ] Create incident with severity and impact
- [ ] Create feature request with business value
- [ ] Create items with minimal fields (defaults work)

**Display and Filtering:**
- [ ] List empty item list
- [ ] List all items with mixed types
- [ ] Show only bugs (filtered by type)
- [ ] Show only QA tickets (filtered by type)
- [ ] Show only incidents (filtered by type)
- [ ] Show critical/high severity items
- [ ] Show items by status (pending/ongoing/completed/resolved)

**Status Management:**
- [ ] Update item status (all transitions)
- [ ] Mark task as ongoing (sets started_at)
- [ ] Mark bug as resolved (sets resolved_at)
- [ ] Mark incident as closed (sets closed_at)
- [ ] Mark QA ticket as completed (prompts for pass/fail)

**Item Operations:**
- [ ] Delete item (any type)
- [ ] Update item details (priority, notes, tags)
- [ ] Link related items (bug to incident, QA to bug, etc.)
- [ ] Add notes to item
- [ ] Update bug-specific fields (environment, reproducibility)
- [ ] Update QA-specific fields (test result, build version)

**Search and Statistics:**
- [ ] Search across all item types
- [ ] Fuzzy match item IDs/titles
- [ ] Show statistics (type breakdown, weekly trends)
- [ ] Show alerts (critical bugs, long-pending items)
- [ ] Calculate average completion times per type

**Data Integrity:**
- [ ] Handle missing tasks.json
- [ ] Handle corrupt JSON
- [ ] Validate item type on creation
- [ ] Validate status transitions
- [ ] Handle bidirectional linking correctly
- [ ] Update statistics on item creation/deletion

**Display Formatting:**
- [ ] Date formatting is human-readable
- [ ] Priority/severity sorting works correctly
- [ ] Duration calculations are accurate
- [ ] Type-specific icons display correctly
- [ ] Related items show correctly
- [ ] Multi-type listings are properly grouped

**Edge Cases:**
- [ ] Handle items with missing optional fields
- [ ] Handle very long titles/descriptions
- [ ] Handle special characters in titles
- [ ] Handle empty related_tickets array
- [ ] Handle migration from v1.0 to v2.0 format
