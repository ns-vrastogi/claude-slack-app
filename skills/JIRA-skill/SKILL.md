# JIRA Deployment Ticket Skill

## Metadata
- **Skill Name**: `JIRA-skill`
- **Purpose**: Create JIRA ENG Deployment tickets for ECGW Ansible release tag promotion and move them to "In Progress" status
- **Execution Type**: JIRA REST API v3 via `curl -k`
- **MCP Tools**: Use `mcp__JIRA__` prefixed tools for reads; use `curl` for create/transition (handles custom fields better)

## Configuration
- **JIRA Base URL**: `https://netskope.atlassian.net`
- **Credentials File**: `~/mcp-atlassian.env`
- **Auth**: Basic auth with `JIRA_USERNAME` and `JIRA_API_TOKEN` from env file
- **API Version**: REST API v3 (uses Atlassian Document Format for rich text)

## Reference Ticket
- **Template Ticket**: ENG-744469
- **Summary Pattern**: `Ansible release tag(<VERSION>) promotion for ECGW self service deployment to R<RELEASE>`
- **Description Pattern**: Same as summary with period at end

---

## Required User Inputs

When this skill is invoked, collect the following from the user:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `VERSION` | The Ansible release tag version (x.y.z format) | `134.0.3` |
| `RELEASE` | The release identifier (Rxxx format) | `R134` |
| `DATACENTER` | The datacenter for deployment (optional, default: NYC3) | `NYC3` |
| `LINK_TICKET` | A ticket to link as "Relates" (optional, default: ENG-744469) | `ENG-744469` |

### Transition Inputs (for moving to "In Progress")

Collect these BEFORE performing the transition in Step 3:

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| `PRE_PROD_STACKS` | Pre-Prod stacks where service was certified | Betaskope (`22965`), Devint (`22966`), Other (`22967`) | Ask user |
| `STAGING_STACKS` | Staging stacks where service was certified | stglocal (`22968`), sjc1clone (`22969`), stg01 (`22970`), Other (`22971`) | Ask user |
| `TEST_RESULTS` | Test results description text | Free text (will be converted to ADF) | Ask user |

**IMPORTANT**:
- If user selects "Other" for Pre-Prod or Staging stacks, they MUST specify which stacks. Otherwise JIRA will reject the transition with: "Please add which stacks was the services certified through, if 'Other' is selected"
- Present the options to the user and let them choose. Do NOT hardcode or randomly select values.

---

## Workflow

### Step 1: Read Credentials
```bash
JIRA_TOKEN=$(grep JIRA_API_TOKEN ~/mcp-atlassian.env | cut -d= -f2-)
```

### Step 2: Create the Deployment Ticket

Use `curl -k` with REST API v3. The payload must include both `update` (for issuelinks) and `fields` sections.

```bash
JIRA_TOKEN=$(grep JIRA_API_TOKEN ~/mcp-atlassian.env | cut -d= -f2-)
curl -k -s -X POST "https://netskope.atlassian.net/rest/api/3/issue" \
  -u "your-username@your-company.com:${JIRA_TOKEN}" \
  -H "Content-Type: application/json" -d '{
  "update": {
    "issuelinks": [
      {
        "add": {
          "type": {"name": "Relates"},
          "outwardIssue": {"key": "<LINK_TICKET>"}
        }
      }
    ]
  },
  "fields": {
    "project": {"key": "ENG"},
    "issuetype": {"id": "10940"},
    "summary": "Ansible release tag(<VERSION>) promotion for ECGW self service deployment to <RELEASE>",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Ansible release tag(<VERSION>) promotion for ECGW self service deployment to <RELEASE>."
            }
          ]
        }
      ]
    },
    "priority": {"id": "3"},
    "assignee": {"accountId": "your-jira-account-id"},
    "components": [{"id": "30756"}],
    "customfield_17018": {"id": "22978"},
    "customfield_20803": [{"id": "22961"}],
    "customfield_20823": "<VERSION>",
    "customfield_17280": [{"id": "<DATACENTER_ID>"}],
    "customfield_23296": {"id": "26378"},
    "customfield_20810": "<START_DATE>",
    "customfield_20811": "<END_DATE>"
  }
}'
```

### Step 3: Collect Transition Inputs

**Before transitioning, ask the user for the following:**

1. **Pre-Prod Stacks** - Present these options:
   - Betaskope (id: `22965`)
   - Devint (id: `22966`)
   - Other (id: `22967`) — ⚠️ If selected, user must specify which stacks

2. **Staging Stacks** - Present these options:
   - stglocal (id: `22968`)
   - sjc1clone (id: `22969`)
   - stg01 (id: `22970`)
   - Other (id: `22971`) — ⚠️ If selected, user must specify which stacks

3. **Test Results** - Ask for a description of test results (free text, e.g., "Ansible config promotion - no functional testing required")

### Step 4: Transition to "In Progress"

Transition ID: `11` (Open → In Progress)

Replace `<PRE_PROD_ID>`, `<STAGING_ID>`, and `<TEST_RESULTS_TEXT>` with user-provided values from Step 3.

```bash
curl -k -s -X POST "https://netskope.atlassian.net/rest/api/3/issue/<TICKET_KEY>/transitions" \
  -u "your-username@your-company.com:${JIRA_TOKEN}" \
  -H "Content-Type: application/json" -d '{
  "transition": {"id": "11"},
  "fields": {
    "customfield_20817": [{"id": "<PRE_PROD_ID>"}],
    "customfield_20818": [{"id": "<STAGING_ID>"}],
    "customfield_20819": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "<TEST_RESULTS_TEXT>"
            }
          ]
        }
      ]
    }
  }
}'
```

### Step 5: Verify

Use MCP tool to confirm status:
```
mcp__JIRA__jira_get_issue(issueKey="<TICKET_KEY>", fields=["summary", "status"])
```

---

## Custom Field Reference

### Creation Fields (in `fields` section)

| Field ID | Name | Type | Value Used |
|----------|------|------|------------|
| `project` | Project | Object | `{"key": "ENG"}` |
| `issuetype` | Issue Type | Object | `{"id": "10940"}` (Deployment) |
| `priority` | Priority | Object | `{"id": "3"}` (Major) |
| `assignee` | Assignee | Object | `{"accountId": "your-jira-account-id"}` (Vishal Rastogi) |
| `components` | Components | Array | `[{"id": "30756"}]` (IPSec GRE Tunnel Steering) |
| `customfield_17018` | Deployment Type | Object | `{"id": "22978"}` (Scheduled deployment) |
| `customfield_20803` | Customer/Service Impact | Array | `[{"id": "22961"}]` (No downtime / No inline impact / No customer action required) |
| `customfield_20823` | Release Version | String | The VERSION value (e.g., `"134.0.3"`) |
| `customfield_17280` | Datacenters | Array | See Datacenter ID mapping below |
| `customfield_23296` | Business Hours | Object | `{"id": "26378"}` (No) |

### Deployment Date Fields (by region)

Dates must be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.000-0800`

| Region | Start Date Field | End Date Field |
|--------|-----------------|----------------|
| APAC | `customfield_20806` | `customfield_20807` |
| EU | `customfield_20808` | `customfield_20809` |
| US East | `customfield_20810` | `customfield_20811` |
| US West | `customfield_20812` | `customfield_20813` |
| AUS | `customfield_21276` | `customfield_21277` |

**Region-to-Datacenter mapping**: Use the deployment date fields that match the datacenter region:
- NYC3 → US East (`customfield_20810`, `customfield_20811`)
- Add other datacenter mappings as needed

### Datacenter IDs

| Datacenter | ID |
|-----------|-----|
| NYC3 | `25111` |

**Note**: For other datacenters, fetch available options:
```bash
curl -k -s -u "your-username@your-company.com:${JIRA_TOKEN}" \
  "https://netskope.atlassian.net/rest/api/3/issue/createmeta/ENG/issuetypes/10940?expand=projects.issuetypes.fields" \
  | python3 -m json.tool | grep -A5 "customfield_17280"
```

### Transition Fields (for "In Progress")

| Field ID | Name | Allowed Values |
|----------|------|---------------|
| `customfield_20817` | Pre-Prod Stacks | Betaskope (`22965`), Devint (`22966`), Other (`22967`) |
| `customfield_20818` | Staging Stacks | stglocal (`22968`), sjc1clone (`22969`), stg01 (`22970`), Other (`22971`) |
| `customfield_20819` | Test Results | ADF format text (see below) |

**IMPORTANT**: Do NOT select "Other" for stacks unless you also specify which stacks in a separate field. Use specific stack values (Betaskope/stglocal) to avoid validation errors.

### Issue Links (in `update` section)

Issue links MUST go in the `update` section, NOT in `fields`:
```json
"update": {
  "issuelinks": [
    {
      "add": {
        "type": {"name": "Relates"},
        "outwardIssue": {"key": "ENG-744469"}
      }
    }
  ]
}
```

---

## Atlassian Document Format (ADF)

For any rich text field in JIRA API v3, use ADF instead of plain strings:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Your text here"
        }
      ]
    }
  ]
}
```

---

## Date Handling

- Default start date: Today at 10:00 AM PST (`YYYY-MM-DDT10:00:00.000-0800`)
- Default end date: Tomorrow at 10:00 AM PST
- Format: ISO 8601 with timezone offset
- Adjust timezone offset for PST (-0800) or PDT (-0700) based on current daylight saving

---

## Error Handling

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Please add planned deployment dates" | Missing date fields for the datacenter's region | Add the correct region date fields |
| "Link tickets that associated with this deployment ticket" | Missing issuelinks | Add issuelinks in `update` section |
| "Field does not support update 'issuelinks'" | issuelinks in `fields` section | Move to `update` section |
| "Operation value must be an Atlassian Document" | Plain string in ADF field | Convert to ADF format |
| "Please add which stacks was the services certified through, if 'Other' is selected" | Selected "Other" for stacks | Use specific stack values (Betaskope/stglocal) |

---

## Complete Example

**User says**: "Create ECGW deployment ticket for version 135.0.1 release R135"

**Execution**:

1. Parse: VERSION=`135.0.1`, RELEASE=`R135`, DATACENTER=NYC3 (default), LINK_TICKET=ENG-744469 (default)
2. Calculate dates: today 10AM PST → tomorrow 10AM PST
3. Create ticket via curl with all fields
4. Extract ticket key from response
5. **Ask user for transition inputs**:
   - "Which Pre-Prod stacks? Options: Betaskope, Devint, Other"
   - "Which Staging stacks? Options: stglocal, sjc1clone, stg01, Other"
   - "What are the test results? (e.g., 'Ansible config promotion - no functional testing required')"
6. Transition to In Progress via curl using user-provided values
7. Verify via MCP tool
8. Report: "Created ENG-XXXXXX and moved to In Progress"
