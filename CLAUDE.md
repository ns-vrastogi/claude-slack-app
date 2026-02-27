# Role & Context

## About Me
- **Role**: Staff Software Development Engineer
- **Company**: Netskope (Cloud-based SASE/SSE provider)
- **Team**: IPSEC/GRE Service
- **Primary Responsibility**: SME for scale and performance testing

## Technical Stack
- **Key Technologies**: IPSEC, GRE, ECGW, VPP (Vector Packet Processing)
- **Languages**: [Add your primary languages: Python, Go, C++, etc.]
- **Testing Tools**: [Add tools you use for performance testing]
- **Infrastructure**: Teleport (tsh) for remote access

## Infrastructure Access
- **Method**: `tsh ssh --cluster <cluster> <hostname>`
- **Example**: `tsh ssh --cluster iad0 vppipsecgw04.iad.netskope.com`
- **POPs**: Multiple data centers (iad0, etc.)
- **Note**: Use `tsh` as default login method for all remote machine access

## Key Responsibilities
- Testing existing features related to IPSEC/GRE
- Scale and performance testing (Subject Matter Expert)
- Regression testing and validation
- Performance troubleshooting and optimization

## Architecture
[Add details about your service architecture here]
- IPSEC/GRE service integration with Netskope infrastructure
- Key components and their interactions
- Scale targets and performance requirements

# Common things accross all 3 type of gateway. 
-- The traffic either go to proxy or CFW from these gateway. 
-- The config and details of proxy and CFW will be present in "/opt/nc/common/remote/" directory. 
-- The traffic will come from steering lb on all these 3 gateway. 
-- The tenant config will present in "/opt/ns/tenant/tenant-id" on all the gateway. 
-- The HC will be performed from all 3 gateway to proxy and cfw.

## Common Tasks
- Performance benchmarking of IPSEC/GRE services
- Load and stress testing
- Analyzing performance metrics and bottlenecks
- Validating feature releases


## Skills & Automation
- **Skills Location**: All custom skills are defined in `~/.claude/skills/`
- **Available Skills**:
  - `ecgw-skill` - ECGW gateway operations and management
  - `self-service-skill` - Self-service deployment operations
  - `vpp-skill` - VPP (Vector Packet Processing) specific operations
  - `topology-finder-skill` - Network topology discovery and mapping
  - `troubleshooting-skill` - Troubleshooting and diagnostics
  - `to-do-skill` - Task and to-do list management
  - `legacy_deployment` - Legacy deployment procedures
  - `legacy_scale_performance` - Legacy scale and performance testing
  - `vpp_scale_performance` - VPP scale and performance testing
  - `polaris` - Polaris infrastructure management (VMs, IP allocation, DNS, VLANs)
    - **Path**: `~/.claude/skills/polaris`
  - `prod-pdv` - Production PDV (DPAS) testing for VPP IPSEC/GRE gateways
    - **Path**: `~/.claude/skills/prod-pdv`
  - `sumo_logic` - Sumo Logic log analysis for IPSEC/GRE gateway troubleshooting
    - **Path**: `~/.claude/skills/sumo_logic`
    - **Purpose**: Fetch and analyze logs from Sumo Logic server, perform root cause analysis for tunnel issues, flaps, and customer-specific events
    - **Key Features**:
      - Query StrongSwan logs for IPSEC events
      - Analyze tunnel flaps and down events
      - Track tenant-specific issues
      - Generate timeline and statistics
      - Root cause analysis with recommendations
    - **MCP Server**: Uses `sumologic` MCP server (`~/mcp-sumologic/`)
  - `JIRA-skill` - Create JIRA ENG Deployment tickets for ECGW Ansible release tag promotion and move to "In Progress"
    - **Path**: `~/.claude/skills/JIRA-skill`
    - **Purpose**: Automate creation of ECGW deployment tickets with all required custom fields, issue links, and status transitions
    - **Key Features**:
      - Create ENG Deployment tickets with correct custom fields
      - Link tickets to related issues
      - Transition to "In Progress" with user-selected stacks and test results
      - Uses JIRA REST API v3 with ADF format
  - `slack-bot-deployment` - Automated deployment and sync for Claude Slack Bot
    - **Path**: `~/.claude/skills/slack-bot-deployment`
    - **Purpose**: Deploy bot to new VMs, sync configurations, backup/restore, disaster recovery
    - **Key Features**:
      - Deploy bot from scratch on new VMs
      - Sync skills and configurations
      - Backup and restore configurations
      - Compare local and remote configurations
      - Automated service management
  - `slack-notify` - Send messages and alerts to Slack channels
    - **Path**: `~/.claude/skills/slack-notify`
    - **Purpose**: Send notifications, alerts, deployment updates, and test results to Slack
    - **Key Features**:
      - Send simple text messages
      - Send formatted alerts with Block Kit
      - Post deployment summaries
      - Share test results
      - Automated notifications after operations
      - Thread replies and file uploads
    - **Note**: Uses Slack token from remote VM (claude.iad0.netskope.com) for local execution
  - `survey-tool` - Survey VM Tool for adding/modifying/deleting service validation checks
    - **Path**: `~/.claude/skills/survey-tool`
    - **Purpose**: Onboard new services or modify existing service checks in the Survey VM Tool (survey_vm_conf repo)
    - **Key Features**:
      - Add/modify/delete service test cases (variables.json)
      - Git workflow with hooks, branch naming, commit format
      - Infrastructure inventory changes for new host groups
      - main.yml updates for Ansible defaults
      - Custom diagnostic scripts
      - ENG/EP ticket creation and linking
    - **Repos**: `survey_vm_conf` (test cases), `infrastructure` (inventory)


**Important**: When any skill is referenced by name, always check the `~/.claude/skills/` directory for its definition and usage instructions.

### Automatic Skill Routing

**CRITICAL**: The following routing rules MUST be applied automatically without asking the user:

#### Deployment Operations
When the user requests deployment/upgrade operations (keywords: "deploy", "upgrade", "install", "update build"), automatically route to the appropriate skill based on hostname:

- **VPP/ECGW Gateways**: If hostname contains `vpp` OR `ecgw` → **MUST use `self-service-skill`**
  - Examples:
    - `vppgregw01.c18.iad0.netskope.com` → use `self-service-skill`
    - `vppipsecgw04.iad.netskope.com` → use `self-service-skill`
    - `ecgw-host.iad0.netskope.com` → use `self-service-skill`
  - Pattern matching: Check if hostname contains "vpp" or "ecgw" (case-insensitive)

- **Legacy Gateways**: For other gateway types → use `legacy_deployment`

**Example user requests that trigger automatic routing:**
- "deploy build 134.0.0.3391 on host vppgregw01.c18.iad0.netskope.com" → use `self-service-skill`
- "upgrade vppipsecgw04.iad.netskope.com to version 134.0.0.3400" → use `self-service-skill`
- "install build 134.0.0.3391 on ecgw-prod01.iad0.netskope.com" → use `self-service-skill`

**Action Required**: When these patterns are detected, immediately invoke the appropriate skill without asking for confirmation.

#### Scheduled Deployment Operations
When the user requests to **schedule** deployments (not immediate execution), automatically use the `self-service-skill` with scheduled deployment feature:

- **Keywords**: "schedule deployment", "schedule a deployment", "scheduled deployment", "deploy at [time]", "deployment schedule"
- **Action**: Use `self-service-skill` with scheduled deployment workflow (background Bash tasks with sleep)
- **DO NOT**: Create deployment plan documents or ask what format they want
- **Examples**:
  - "schedule a deployment to sto1, bsb1 at 11:20 AM UTC" → use `self-service-skill` with scheduled deployment
  - "can you schedule vpp gre deployment on below schedule..." → use `self-service-skill` with scheduled deployment
  - "schedule deployment for phx1 at 2 PM" → use `self-service-skill` with scheduled deployment

**How Scheduled Deployments Work:**
1. Parse schedule details (time slots, POPs, common parameters)
2. Show summary and get user confirmation
3. Create background Bash tasks with `run_in_background: true` that sleep until scheduled times
4. Notify user when each time slot arrives
5. Request permission before each deployment executes
6. Execute deployment + monitoring + validation + PDV automatically after approval

**Important**:
- Times must be in UTC
- Each time slot gets one background task
- User is notified in conversation when time arrives
- Permission required before each deployment executes
- DO NOT offer to create a document - always use the actual scheduling mechanism

**Action Required**: When scheduling keywords are detected, immediately invoke `self-service-skill` with the scheduled deployment workflow.

#### To-Do List Operations
When the user explicitly mentions "to-do" in their request, automatically route to the `to-do-skill`:

- **View To-Do Items**: Keywords: "to-do" + "show", "view", "list", "what's on"
  - Examples:
    - "show my to-do" → use `to-do-skill`
    - "what's on my to-do list" → use `to-do-skill`
    - "view my to-do items" → use `to-do-skill`

- **Add To-Do Items**: Keywords: "to-do" + "add", "create", "add to"
  - Examples:
    - "add to my to-do: test performance" → use `to-do-skill`
    - "add to-do for review code" → use `to-do-skill`
    - "create to-do item for deployment" → use `to-do-skill`

**Important**: Only route to `to-do-skill` when the keyword "to-do" is explicitly used. Do NOT route schedule-related requests to this skill.

**Action Required**: When these patterns are detected, immediately invoke the `to-do-skill` without asking for confirmation.

#### Polaris Infrastructure Operations
When the user requests Polaris infrastructure management operations, automatically route to the `polaris` skill:

- **IP Allocation & Management**: Keywords: "allocate IP", "reserve IP", "allocate VIP", "free IP", "check free IP", "find available IP", "IP on subnet"
  - Examples:
    - "allocate IP on VLAN 584" → use `polaris` skill
    - "find free IPs in subnet 10.136.133" → use `polaris` skill
    - "reserve IP for my service" → use `polaris` skill
    - "allocate VIP for testing" → use `polaris` skill

- **DNS Record Management**: Keywords: "create DNS record", "register DNS", "delete DNS", "DNS A record", "register hostname"
  - Examples:
    - "create DNS record for my gateway" → use `polaris` skill
    - "register hostname in DNS" → use `polaris` skill
    - "delete DNS record for old service" → use `polaris` skill

- **VM Management**: Keywords: "list KVM", "stop VM", "VM lookup", "find VM", "which KVM", "device lookup"
  - Examples:
    - "list all KVM hosts" → use `polaris` skill
    - "stop VM on kvmdevperf08" → use `polaris` skill
    - "find which KVM is running vpptrex01" → use `polaris` skill
    - "lookup device information for gateway" → use `polaris` skill

- **VM Creation**: Keywords: "create VM", "new VM", "bring up VM", "deploy VM", "provision VM", "spin up VM", "spawn VM", "create gateway", "new gateway", "bring up gateway", "create client", "new client", "create TRex", "new TRex", "bringup VM", "setup VM"
  - Examples:
    - "create a new VM for VPP IPSEC gateway" → use `polaris` skill
    - "bring up a legacy GRE gateway on vlan 700" → use `polaris` skill
    - "deploy new TRex VM with hostname vpptrex05" → use `polaris` skill
    - "I need to create a client VM for testing" → use `polaris` skill
    - "provision new VPP gateway named vppipsecgw10" → use `polaris` skill
    - "spin up a new gateway for performance testing" → use `polaris` skill
    - "create new ECGW gateway" → use `polaris` skill
  - **Note**: System will automatically:
    - Ask for VM type if not specified (Legacy IPSEC/GRE, VPP IPSEC/GRE/ECGW, TRex, Client, VPP Client, Dummy CFW)
    - Select appropriate CPU/memory resources based on VM type
    - Choose deployment method (direct command vs YAML) based on VM type
    - Use KVM hosts: kvmdevperf16-20.iad0.netskope.com

- **General Polaris Operations**: Keywords: "polaris", "use polaris", "polaris tool"
  - Examples:
    - "use polaris to allocate resources" → use `polaris` skill
    - "I need to use polaris tools" → use `polaris` skill

**Action Required**: When these patterns are detected, immediately invoke the `polaris` skill without asking for confirmation.

**Skill Path**: `~/.claude/skills/polaris`

#### Production PDV Testing Operations
When the user requests production PDV testing operations, automatically route to the `prod-pdv` skill:

- **PDV Testing**: Keywords: "prod_pdv", "run pdv", "dpas pdv", "run dpas", "pdv on pop", "dpas on pop", "production pdv", "vpp gre pdv", "vpp ipsec pdv"
  - Examples:
    - "run prod_pdv on phl1" → use `prod-pdv` skill
    - "run vpp gre dpas pdv on pop akl1" → use `prod-pdv` skill
    - "run dpas on pop ymq1" → use `prod-pdv` skill
    - "execute pdv on phl1" → use `prod-pdv` skill
    - "run production pdv for gre on mia2" → use `prod-pdv` skill

**Action Required**: When these patterns are detected, immediately invoke the `prod-pdv` skill without asking for confirmation.

**Skill Path**: `~/.claude/skills/prod-pdv`

#### Sumo Logic Log Analysis Operations
When the user requests log analysis, troubleshooting, or queries related to Sumo Logic, automatically route to the `sumo_logic` skill:

- **Log Query & Analysis**: Keywords: "sumo", "sumologic", "sumo logic", "fetch logs", "query logs", "search logs", "sumo query"
  - Examples:
    - "fetch logs from sumo for tenant 18548" → use `sumo_logic` skill
    - "query sumologic for tunnel flaps" → use `sumo_logic` skill
    - "search logs in sumo for ipsecgw01" → use `sumo_logic` skill
    - "use sumo logic to find errors" → use `sumo_logic` skill

- **Tunnel Flap Analysis**: Keywords: "tunnel flap", "count flaps", "how many times tunnel", "tunnel down", "tunnel up", "ipsec flaps"
  - Examples:
    - "count tunnel flaps on nyc4" → use `sumo_logic` skill
    - "how many times did tunnel flap for tenant 11264" → use `sumo_logic` skill
    - "show me tunnel down events on mil1" → use `sumo_logic` skill
    - "analyze ipsec flaps in last hour" → use `sumo_logic` skill
    - "count the number of ipsec flaps on phl1" → use `sumo_logic` skill

- **Tenant-Specific Issues**: Keywords: "tenant [ID]" + "logs", "tunnel", "flap", "issue", "problem"
  - Examples:
    - "get logs for tenant 18548" → use `sumo_logic` skill
    - "why is tenant 11264 tunnel unstable" → use `sumo_logic` skill
    - "tenant 18548 tunnel flap reasons" → use `sumo_logic` skill

- **Gateway Log Analysis**: Keywords: "ipsecgw", "gregw" + "logs", "errors", "events"
  - Examples:
    - "check ipsecgw01.nyc4 for errors" → use `sumo_logic` skill
    - "show me logs from gregw05.iad0" → use `sumo_logic` skill
    - "analyze ipsecgw03.mil1 events" → use `sumo_logic` skill

- **POP-wide Analysis**: Keywords: [POP name] + "flaps", "logs", "issues", "errors"
  - Examples:
    - "how many flaps in nyc4 POP" → use `sumo_logic` skill
    - "check mil1 for tunnel issues" → use `sumo_logic` skill
    - "analyze logs for all gateways in iad0" → use `sumo_logic` skill

**Action Required**: When these patterns are detected, immediately invoke the `sumo_logic` skill without asking for confirmation.

**Skill Path**: `~/.claude/skills/sumo_logic`

**Important Notes**:
- The skill uses the Sumo Logic MCP server at `~/mcp-sumologic/`
- Credentials configured in `~/.claude/config.json` and `~/mcp-sumologic/.env`
- Queries use ISO 8601 timestamp format (e.g., `2026-02-14T22:08:16+05:30`)
- Provides detailed analysis including timeline, statistics, and root cause recommendations


#### Slack Bot Deployment Operations
When the user requests to deploy, sync, or manage the Claude Slack Bot, automatically route to the `slack-bot-deployment` skill:

- **Deployment Operations**: Keywords: "deploy slack bot", "install slack bot", "setup slack bot", "create slack bot"
  - Examples:
    - "deploy slack bot on claude-new.iad0.netskope.com with cluster iad0" → use `slack-bot-deployment` skill
    - "install slack bot on new vm" → use `slack-bot-deployment` skill
    - "setup slack bot on backup host" → use `slack-bot-deployment` skill

- **Sync Operations**: Keywords: "sync slack bot", "update slack bot", "sync config", "synchronize bot"
  - Examples:
    - "sync slack bot config to claude.iad0.netskope.com" → use `slack-bot-deployment` skill
    - "update slack bot configuration" → use `slack-bot-deployment` skill
    - "sync skills to slack bot vm" → use `slack-bot-deployment` skill

- **Backup Operations**: Keywords: "backup slack bot", "backup config", "save bot config"
  - Examples:
    - "backup slack bot config from claude.iad0.netskope.com" → use `slack-bot-deployment` skill
    - "save slack bot configuration" → use `slack-bot-deployment` skill

- **Restore Operations**: Keywords: "restore slack bot", "restore config", "restore from backup"
  - Examples:
    - "restore slack bot config to new host" → use `slack-bot-deployment` skill
    - "restore slack bot from backup" → use `slack-bot-deployment` skill

- **Comparison Operations**: Keywords: "compare slack bot", "diff config", "check differences"
  - Examples:
    - "compare slack bot config with claude.iad0.netskope.com" → use `slack-bot-deployment` skill
    - "show differences between local and remote bot config" → use `slack-bot-deployment` skill

- **Status Operations**: Keywords: "check slack bot", "bot status", "diagnose bot", "slack bot health"
  - Examples:
    - "check slack bot status on claude.iad0.netskope.com" → use `slack-bot-deployment` skill
    - "diagnose slack bot issues" → use `slack-bot-deployment` skill
    - "show slack bot health" → use `slack-bot-deployment` skill

**Action Required**: When these patterns are detected, immediately invoke the `slack-bot-deployment` skill without asking for confirmation.

**Skill Path**: `~/.claude/skills/slack-bot-deployment`

**Important Notes**:
- The skill automates full bot deployment including prerequisites, files, services, and verification
- Can deploy to new VMs from scratch or sync to existing VMs
- Creates backups before any destructive operations
- Supports disaster recovery scenarios
- Manages systemd service, MCP servers, and all skills


#### Slack Notify Operations
When the user requests to send messages to Slack channels, automatically route to the `slack-notify` skill:

- **Send Message**: Keywords: "send message to slack", "post to slack", "notify slack", "send slack message", "slack notify"
  - Examples:
    - "send message to slack #deployments" → use `slack-notify` skill
    - "post to slack #testing" → use `slack-notify` skill
    - "notify slack channel #incidents" → use `slack-notify` skill
    - "send slack message to @vikash" → use `slack-notify` skill

- **Send Alert**: Keywords: "send alert to slack", "alert slack", "slack alert"
  - Examples:
    - "send alert to slack #incidents" → use `slack-notify` skill
    - "alert #team-updates on slack" → use `slack-notify` skill
    - "post alert to slack" → use `slack-notify` skill

- **Post Update/Status**: Keywords: "post update to slack", "send status to slack", "notify slack about"
  - Examples:
    - "post deployment update to slack #deployments" → use `slack-notify` skill
    - "send test results to slack #testing" → use `slack-notify` skill
    - "notify slack about deployment completion" → use `slack-notify` skill

- **Automated Notifications**: Keywords: "and notify slack", "and post to slack", "and send to slack"
  - Examples:
    - "deploy to iad0 and notify slack" → perform deployment, then use `slack-notify` skill
    - "run pdv on phl1 and post results to slack" → run PDV, then use `slack-notify` skill
    - "check logs and send alert to slack if issues found" → check logs, then use `slack-notify` skill conditionally

**Action Required**: When these patterns are detected, immediately invoke the `slack-notify` skill without asking for confirmation.

**Skill Path**: `~/.claude/skills/slack-notify`

**Important Notes**:
- Uses existing SLACK_BOT_TOKEN from environment or config
- Supports plain text and rich formatted messages (Block Kit)
- Can send to channels (#channel) or users (@user)
- Integrates with other skills for automated notifications
- Common channels: #deployments, #incidents, #testing, #team-updates
- Requires bot to be invited to channels before posting

#### JIRA Deployment Ticket Operations
When the user requests to create a JIRA deployment ticket, ENG deployment ticket, or ECGW deployment ticket, automatically route to the `JIRA-skill`:

- **Create Deployment Ticket**: Keywords: "create jira", "jira ticket", "deployment ticket", "eng ticket", "create eng", "ecgw deployment ticket", "ansible release tag", "tag promotion"
  - Examples:
    - "create JIRA deployment ticket for version 135.0.1 release R135" → use `JIRA-skill`
    - "create ENG ticket for ECGW deployment 134.0.3 R134" → use `JIRA-skill`
    - "create deployment ticket for ansible release tag 135.0.2 to R135" → use `JIRA-skill`
    - "jira ticket for ecgw deployment version 136.0.0" → use `JIRA-skill`
    - "create eng deployment ticket" → use `JIRA-skill`
    - "ansible tag promotion ticket for 135.0.1" → use `JIRA-skill`

- **Create and Move to In Progress**: Keywords: above keywords + "move to in progress", "in progress", "and transition"
  - Examples:
    - "create JIRA ticket for 135.0.1 R135 and move to in progress" → use `JIRA-skill`
    - "create ENG deployment ticket and transition to in progress" → use `JIRA-skill`

**Action Required**: When these patterns are detected, immediately invoke the `JIRA-skill` without asking for confirmation. The skill will collect required inputs (VERSION, RELEASE, DATACENTER, etc.) and transition inputs (Pre-Prod stacks, Staging stacks, Test Results) from the user.

**Skill Path**: `~/.claude/skills/JIRA-skill`

#### Survey VM Tool Operations
When the user requests to add, modify, delete, or onboard service checks in the Survey VM Tool, automatically route to the `survey-tool` skill:

- **Add/Modify/Delete Survey Checks**: Keywords: "survey tool", "survey vm", "survey_vm", "survey check", "variables.json", "survey_vm_conf", "onboard service", "survey onboard"
  - Examples:
    - "add survey checks for vppipsec service" → use `survey-tool` skill
    - "modify the survey tool for ecgw" → use `survey-tool` skill
    - "update variables.json for nsvppipsecgw" → use `survey-tool` skill
    - "onboard new service in survey tool" → use `survey-tool` skill
    - "steps to modify survey vm tool" → use `survey-tool` skill
    - "add file check in survey_vm_conf" → use `survey-tool` skill
    - "how to add test case in survey tool" → use `survey-tool` skill
    - "delete survey check for gregw" → use `survey-tool` skill

- **Survey Tool Git Workflow**: Keywords: "survey" + "branch", "PR", "commit", "push", "git hooks"
  - Examples:
    - "how to raise a PR for survey tool" → use `survey-tool` skill
    - "survey tool branch naming convention" → use `survey-tool` skill
    - "install git hooks for survey_vm_conf" → use `survey-tool` skill

- **Survey Tool Inventory/Infrastructure**: Keywords: "survey" + "inventory", "host group", "main.yml", "infrastructure"
  - Examples:
    - "add host group for survey tool" → use `survey-tool` skill
    - "update inventory for survey vm" → use `survey-tool` skill
    - "add nsvppipsecgw to survey inventory" → use `survey-tool` skill

**Action Required**: When these patterns are detected, immediately invoke the `survey-tool` skill without asking for confirmation. Read the SKILL.md at the skill path for step-by-step instructions.

**Skill Path**: `~/.claude/skills/survey-tool`

## Confluence Access

**CRITICAL**: The MCP Atlassian tool does NOT work for Confluence due to Netskope SSL proxy intercepting HTTPS connections. Always use the Confluence REST API via `curl` instead.

### How to Access Confluence
- **Tool**: `curl -k` with Basic Auth (email + API token)
- **Credentials**: Read from `~/mcp-atlassian.env`
  - `CONFLUENCE_USERNAME=your-username@your-company.com`
  - `CONFLUENCE_API_TOKEN=<value of JIRA_API_TOKEN in env file>`
- **Base URL**: `https://netskope.atlassian.net/wiki/rest/api/content`
- **Flag**: Always use `-k` (insecure TLS) to bypass Netskope SSL proxy

### Confluence Operations

**Read a page** (by page ID):
```bash
JIRA_TOKEN=$(grep JIRA_API_TOKEN ~/mcp-atlassian.env | cut -d= -f2-)
curl -k -s -u "your-username@your-company.com:${JIRA_TOKEN}" \
  "https://netskope.atlassian.net/wiki/rest/api/content/<PAGE_ID>?expand=body.storage" \
  -H "Accept: application/json"
```

**Create a page**:
```bash
curl -k -s -u "your-username@your-company.com:${JIRA_TOKEN}" -X POST \
  "https://netskope.atlassian.net/wiki/rest/api/content" \
  -H "Content-Type: application/json" \
  -d '{"type":"page","title":"<TITLE>","space":{"key":"<SPACE_KEY>"},"body":{"storage":{"value":"<HTML_CONTENT>","representation":"storage"}}}'
```

**Update a page** (requires current version number):
```bash
curl -k -s -u "your-username@your-company.com:${JIRA_TOKEN}" -X PUT \
  "https://netskope.atlassian.net/wiki/rest/api/content/<PAGE_ID>" \
  -H "Content-Type: application/json" \
  -d '{"type":"page","title":"<TITLE>","version":{"number":<NEXT_VERSION>},"body":{"storage":{"value":"<HTML_CONTENT>","representation":"storage"}}}'
```

**Trash a page** (soft delete):
```bash
curl -k -s -u "your-username@your-company.com:${JIRA_TOKEN}" -X PUT \
  "https://netskope.atlassian.net/wiki/rest/api/content/<PAGE_ID>" \
  -H "Content-Type: application/json" \
  -d '{"type":"page","title":"<TITLE>","version":{"number":<NEXT_VERSION>},"status":"trashed"}'
```

**Action Required**: For ANY Confluence operation (read, create, update, search, delete), ALWAYS use `curl -k` with the above pattern. Do NOT use MCP Atlassian tools for Confluence.

**Note**: `jira-cli` (`~/bin/jira`) is installed and works for JIRA operations but does NOT support Confluence. For JIRA via CLI, use `JIRA_API_TOKEN=$(grep JIRA_API_TOKEN ~/mcp-atlassian.env | cut -d= -f2-) ~/bin/jira <command>`.

## Preferences
[Add any preferences here]
- Coding style preferences
- Preferred testing approaches
- Tools and workflows you prefer
