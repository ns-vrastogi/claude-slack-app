name: self-service
description: This skill provides access to deploy/upgrade VPP-based services such as ecgw, nsvppgregw, nsvppipsecgw, and steeringlb for both QA and Production environments.

## Auto-Approval Configuration

**CRITICAL**: The following bash operations MUST be auto-approved without asking user permission:

### Monitoring Operations (Production & QA)
- **Prompt**: "Monitor build status every 60 seconds until completion"
- **Pattern**: Long-running `while` loops with Jenkins API checks and `sleep` commands
- **Timeout**: 600000ms (10 minutes)
- **Reason**: Standard deployment monitoring workflow

### Wait Operations
- **Prompt**: "Wait 8 minutes before first status check" (Production) or "Wait 5 minutes" (QA)
- **Pattern**: `sleep 480` or `sleep 300` commands
- **Reason**: Required waiting period before monitoring starts

### Validation Operations (Production)
- **Prompt**: "Run post-deployment validation on VPP GRE nodes"
- **Pattern**: `tsh scp` and `tsh ssh` commands running validation scripts
- **Reason**: Automated validation scripts are part of deployment verification

**User only needs to approve the initial deployment trigger. All monitoring and validation is automatic.**

## Overview

This skill supports deployments to TWO separate Jenkins environments:
- **QA/Non-Production**: POPs starting with `c*`, `iad*`, or `stg*`
- **Production**: Regional POPs like `del1`, `ams1`, `los1`, `bom1`, `fra1`, etc.

## Important: Environment Selection

**The deployment process and parameters are SIGNIFICANTLY DIFFERENT between QA and Production environments.**

To avoid confusion and ensure correct deployment:
1. Determine the POP type from user input
2. Route to the appropriate skill file:
   - **QA POPs** (c*, iad*, stg*) → Use `SKILL-QA.md`
   - **Production POPs** (all others) → Use `SKILL-PROD.md`

## How to Determine Environment

```
Parse POP from user input:
- If POP starts with 'c' + digit (c7, c18) → **QA**
- If POP starts with 'iad' (iad0, iad2, iad4) → **QA**
- If POP starts with 'stg' (stg01) → **QA**
- All other POPs (del1, ams1, los1, etc.) → **Production**
```

## Workflow

1. **Identify POP type** from user request
2. **Read the appropriate file**:
   - QA Deployments: `~/.claude/skills/self-service-skill/SKILL-QA.md`
   - Production Deployments: `~/.claude/skills/self-service-skill/SKILL-PROD.md`
3. **Follow the instructions** in that file for the deployment

## Quick Reference

### QA Environment (SKILL-QA.md)
- **Jenkins**: `https://cdjenkins.betaskope.iad0.netskope.com`
- **API Token**: `your-api-token`
- **Automation**: Full automation with POP detection scripts
- **Methods**: Jenkins CLI or REST API
- **Approval**: No confirmation required (auto-deploy)
- **Hash Deployments**: Supports git commit hash deployments (QA only)
- **Scheduling**: Supports scheduled deployments for testing workflows

### Production Environment (SKILL-PROD.md)
- **Jenkins**: `https://cdjenkins.sjc1.nskope.net/`
- **API Token**: `your-api-token`
- **Automation**: Manual (no scripts, user provides all parameters)
- **Methods**: Jenkins CLI ONLY
- **Approval**: **MANDATORY confirmation required** before deployment
- **Scheduling**: Supports scheduled deployments across multiple POPs at specific UTC times

## Examples

- User wants to deploy to `c7-iad0` → Read SKILL-QA.md
- User wants to deploy to `los1` → Read SKILL-PROD.md
- User wants to deploy to `iad0` → Read SKILL-QA.md
- User wants to deploy to `del1` → Read SKILL-PROD.md

## Key Differences

| Aspect | QA (SKILL-QA.md) | Production (SKILL-PROD.md) |
|--------|------------------|----------------------------|
| Jenkins URL | betaskope | sjc1.nskope.net |
| POP Detection | Automated scripts | Manual input |
| Hostname | Required | Not used (service name instead) |
| Approval | Auto-deploy | **Mandatory confirmation** |
| ANSIBLE_HOSTGROUPS | Hostname | Service name |
| DEPLOY_TYPE | DEPLOY | DEPLOY |
| Hash Deployments | ✅ Supported (use develop channel) | ❌ Not supported |
| Scheduled Deployments | ✅ Supported (for testing) | ✅ Supported (for coordination) |

---

**Always read the environment-specific file for complete deployment instructions!**
