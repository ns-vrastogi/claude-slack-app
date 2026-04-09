# Self-Service Skill Configuration

**Fill this file in before using the skill. Claude reads it at the start of every deployment.**

---

## Jenkins Credentials

Set these as environment variables in `~/.bashrc` (do NOT hardcode tokens here):

```bash
export JENKINS_PROD_URL="https://your-prod-jenkins.company.com/"
export JENKINS_QA_URL="https://your-qa-jenkins.company.com/"
export JENKINS_USERNAME="your-email@company.com"
export JENKINS_PROD_TOKEN="your-prod-api-token"
export JENKINS_QA_TOKEN="your-qa-api-token"
export GITHUB_TOKEN="your-github-token"   # QA POP detection only
```

---

## Jenkins Job Names

Update these to match your Jenkins job names:

| Service | Production Job | QA Job |
|---------|---------------|--------|
| VPP GRE Gateway | `one_button_nsvppgregw` | `one_button_nsvppgregw` |
| VPP IPSEC Gateway | `one_button_nsvppipsecgw` | `one_button_nsvppipsecgw` |
| ECGW | `one_button_ecgw` | `one_button_ecgw` |
| SteeringLB | `one_button_steeringlb` | `one_button_steeringlb` |

---

## Jenkins Job Parameters

These are the parameters your Jenkins jobs accept. **Edit this section to match your pipeline.**

### Parameters User Always Provides
These are collected from the user every time:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `POPS` | Target POP(s), comma-separated, lowercase | `del1,ams1` |
| `RELEASE` | Build/artifact version | `134.0.8.3068` |
| `ANSIBLE_CONFIG_IMAGE_TAG` | Config image tag | `134.0.14` |
| `TICKET` | Ticket/change reference | `ENG-12345` |

### Parameters Derived from Service Name
These are auto-set based on the service the user requests:

| Parameter | Value | Notes |
|-----------|-------|-------|
| `ANSIBLE_COMPONENT_NAME` | `<service>` | e.g. `nsvppgregw` |
| `ANSIBLE_HOSTGROUPS` | `<service>` | Same as component name in prod |
| `ANSIBLE_CONFIG_IMAGE_NAME` | `<service>-ansible-config` | |

### Fixed Parameters (Production)
These are the same for every production deployment — edit to match your pipeline:

| Parameter | Value | Remove if not applicable |
|-----------|-------|--------------------------|
| `ANSIBLE_ARTIFACTORY_CHANNEL` | `ipsec-gre-production-docker` | Your artifact channel name |
| `ANSIBLE_VERBOSITY` | `2` | Ansible verbosity level |
| `ANSIBLE_CORE_VERSION` | `2.15` | Ansible version |
| `REGIONS` | `America,APAC,Europe` | Your regions |
| `POP_TYPES` | `MP,DP,GCP,EKS` | Your POP types |
| `BYPASS_MONITORING_RESULT` | `YES` | Remove if your pipeline doesn't have this |
| `BYPASS_JIRA` | `YES` | Remove if your pipeline doesn't have this |
| `RUN_QE_PDV` | `DEPLOY_ONLY` | Remove if your pipeline doesn't have this |
| `DEPLOY_TYPE` | `DEPLOY` | |
| `SELECT_ALL_POPS` | *(empty)* | Remove if not applicable |
| `SELECT_ALL_COMPONENTS` | *(empty)* | Remove if not applicable |

### Fixed Parameters (QA)
| Parameter | Value | Remove if not applicable |
|-----------|-------|--------------------------|
| `ANSIBLE_ARTIFACTORY_CHANNEL` | `ipsec-gre-release-docker` | Your QA artifact channel |
| `ANSIBLE_VERBOSITY` | `0` | |
| `SELECT_ALL_POPS` | `Unselect All` | Remove if not applicable |
| `SELECT_ALL_COMPONENTS` | `SELECT_ALL` | Remove if not applicable |
| `BYPASS_JIRA` | `YES` | Remove if not applicable |
| `RUN_QE_PDV` | `DEPLOY_ONLY` | Remove if not applicable |
| `DEPLOY_TYPE` | `DEPLOY` | |

---

## POP Categorization

Update the routing logic in `SKILL.md` if your QA/Production POP naming differs:

```
Current QA POP patterns:  c* (c7, c18), iad0, stg*
Current Prod POP pattern: everything else
```

---

## Adapting for Your Infrastructure

1. **Different job naming**: Update the Job Names table above
2. **Fewer parameters**: Delete rows from the Fixed Parameters tables
3. **Different parameter names**: Rename the parameters in the tables above — Claude will use these names when building the curl command
4. **Additional parameters**: Add new rows to the tables
5. **Different artifact channels**: Update `ANSIBLE_ARTIFACTORY_CHANNEL` values
6. **Different hostname format**: Update the hostname-to-POP pattern in `SKILL-DEPLOYMENT-FAILURE.md` Step 2
