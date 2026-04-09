# Self-Service Deployment Skill

Deploy VPP-based gateway services (IPSEC/GRE/ECGW/SteeringLB) via Jenkins — directly from your Claude console, no Slack bot required.

---

## Quick Start

### 1. Set environment variables

Add to `~/.bashrc` (or `~/.zshrc`):

```bash
export JENKINS_PROD_URL="https://your-prod-jenkins.company.com/"
export JENKINS_QA_URL="https://your-qa-jenkins.company.com/"
export JENKINS_USERNAME="your-email@company.com"
export JENKINS_PROD_TOKEN="your-prod-api-token"
export JENKINS_QA_TOKEN="your-qa-api-token"

# Optional: for QA POP auto-detection via GitHub inventory
export GITHUB_TOKEN="your-github-token"
```

```bash
source ~/.bashrc
```

### 2. Install Java (Jenkins CLI dependency)

```bash
# macOS
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Linux (Debian/Ubuntu)
sudo apt install openjdk-17-jdk

# Linux (RHEL/CentOS)
sudo yum install java-17-openjdk
```

### 3. Download Jenkins CLI jar

```bash
mkdir -p ~/.claude
curl -o ~/.claude/jenkins-cli.jar "${JENKINS_PROD_URL}/jnlpJars/jenkins-cli.jar"
```

### 4. Edit CONFIG.md for your infrastructure

Open `CONFIG.md` and update:
- **Jenkins job names** — set the correct job name for each service (prod + QA)
- **Job parameters** — add/remove/rename parameters to match your pipeline
- **POP categorization** — update if your QA/prod POP naming differs

This is the only file you need to edit. All skill files read `CONFIG.md` to build Jenkins commands.

### 5. Copy skill to Claude config

```bash
cp -r self-service-skill ~/.claude/skills/
```

### 6. Verify connection

```bash
java -jar ~/.claude/jenkins-cli.jar \
  -s "${JENKINS_PROD_URL}" \
  -auth "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
  version
```

---

## Usage

Start Claude and describe your deployment:

```
Deploy build 134.0.2.3026 on nsvppgregw to los1 with ansible tag 134.0.9, ticket ENG-12345
```

```
Schedule nsvppipsecgw deployment:
  RELEASE: 134.0.2.3026
  TAG: 134.0.9
  TICKET: ENG-12345

  9:30 AM PST → del1, ams1
  2:00 PM PST → bom1
```

---

## Skill Files

| File | Purpose |
|------|---------|
| `CONFIG.md` | **Your configuration** — job names, parameters, POP patterns |
| `SKILL.md` | Entry point — reads CONFIG.md, detects environment, routes to correct file |
| `SKILL-PROD-IMMEDIATE.md` | Production immediate deployments |
| `SKILL-PROD-SCHEDULED.md` | Production scheduled deployments |
| `SKILL-QA.md` | QA deployments (immediate + scheduled) |
| `SKILL-DEPLOYMENT-FAILURE.md` | Failure diagnosis and retry workflow |

---

## Adapting for Your Infrastructure

Everything infrastructure-specific lives in **`CONFIG.md`**:

| What to change | Where in CONFIG.md |
|----------------|--------------------|
| Jenkins job names | "Jenkins Job Names" table |
| Production job parameters | "Fixed Parameters (Production)" table |
| QA job parameters | "Fixed Parameters (QA)" table |
| User-provided parameters | "Parameters User Always Provides" table |
| POP categorization (QA vs Prod) | Note at bottom — then update `SKILL.md` routing |
| QA POP detection repos | "POP Detection" section in `SKILL-QA.md` |
