name: self-service
description: Deploy/upgrade VPP-based gateway services via Jenkins. Supports immediate and scheduled deployments for QA and Production environments.

---

## First-Time Setup

Before using this skill, set the following environment variables in `~/.bashrc` (or `~/.zshrc`):

```bash
# Production Jenkins
export JENKINS_PROD_URL="https://your-prod-jenkins.company.com/"
export JENKINS_PROD_TOKEN="your-prod-api-token"

# QA Jenkins (if separate)
export JENKINS_QA_URL="https://your-qa-jenkins.company.com/"
export JENKINS_QA_TOKEN="your-qa-api-token"

# Common
export JENKINS_USERNAME="your-email@company.com"
export JENKINS_JOB_PREFIX="one_button"   # Job naming pattern: one_button_<service>

# GitHub token (required for QA POP auto-detection only)
export GITHUB_TOKEN="your-github-token"
```

Then run: `source ~/.bashrc`

### Install Required Tools

```bash
# Java (required for Jenkins CLI)
# macOS
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

# Linux
sudo apt install openjdk-17-jdk   # Debian/Ubuntu
sudo yum install java-17-openjdk  # RHEL/CentOS

# Download Jenkins CLI jar
curl -o ~/.claude/jenkins-cli.jar ${JENKINS_PROD_URL}/jnlpJars/jenkins-cli.jar

# Verify
java -jar ~/.claude/jenkins-cli.jar -s ${JENKINS_PROD_URL} -auth ${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN} version
```

---

## Environment Routing

```
Parse POP from user input:
- Starts with 'c' + digit  (c7, c18)  → QA
- Starts with 'iad0'                   → QA
- Starts with 'stg'        (stg01)    → QA
- Anything else            (del1 etc) → Production
```

| Environment | Mode | Skill File | Confirmation |
|-------------|------|-----------|-------------|
| QA (c*, iad0, stg*) | Immediate | `SKILL-QA.md` | Not required |
| QA (c*, iad0, stg*) | Scheduled | `SKILL-QA.md` | Not required |
| Production | **Immediate** | `SKILL-PROD-IMMEDIATE.md` | **Mandatory** |
| Production | **Scheduled** | `SKILL-PROD-SCHEDULED.md` | **Mandatory** |

**Workflow:**
1. Identify POP type from user request
2. If Production — check for "schedule/scheduled/at [time]" keywords:
   - Present → use `SKILL-PROD.md`
   - Absent → use `SKILL-PROD-IMMEDIATE.md`
3. If QA → use `SKILL-QA.md` (handles both immediate and scheduled)

---

## Supported Services

- `nsvppipsecgw` — VPP IPSEC gateway
- `nsvppgregw` — VPP GRE gateway
- `ecgw` — ECGW gateway
- `steeringlb` — Steering Load Balancer

Jenkins job name = `${JENKINS_JOB_PREFIX}_<service>` (e.g., `one_button_nsvppgregw`)

If your Jenkins uses a different job naming convention, update `JENKINS_JOB_PREFIX` accordingly or provide the full job name.
