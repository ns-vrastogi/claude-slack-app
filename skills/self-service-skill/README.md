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
export JENKINS_JOB_PREFIX="one_button"   # job = one_button_<service>

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

### 4. Copy skill to Claude config

```bash
cp -r self-service-skill ~/.claude/skills/
```

### 5. Verify

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
| `SKILL.md` | Entry point — environment detection and routing |
| `SKILL-QA.md` | QA deployments (c*, iad0, stg*) |
| `SKILL-PROD.md` | Production deployments — immediate and scheduled |

---

## Adapting for Your Infrastructure

| What to change | Where |
|----------------|-------|
| Jenkins URLs and tokens | Environment variables (see above) |
| Jenkins job naming pattern | `JENKINS_JOB_PREFIX` env var |
| QA POP detection repos | `SKILL-QA.md` — GitHub repo mapping section |
| Jenkins job parameters | `SKILL-PROD.md` and `SKILL-QA.md` — adjust `-p` flags to match your pipeline |
| POP categorization (QA vs Prod) | `SKILL.md` — routing logic section |
