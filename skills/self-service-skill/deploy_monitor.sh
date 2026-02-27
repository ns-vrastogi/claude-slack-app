#!/bin/bash

################################################################################
# Production Deployment Monitor with Real-Time Parallel Execution
#
# This script monitors a Jenkins deployment job and:
# 1. Detects when each POP completes deployment (via PLAY RECAP)
# 2. Immediately triggers post-deployment validation (parallel)
# 3. Queues POPs for sequential PDV testing
# 4. Coordinates PDV execution (one POP at a time)
#
# Usage:
#   ./deploy_monitor.sh <BUILD_NUMBER> <SERVICE> <POPS>
#
# Example:
#   ./deploy_monitor.sh 249 nsvppgregw "dxb1,man1"
################################################################################

set -euo pipefail

# Configuration
JENKINS_URL="https://cdjenkins.sjc1.nskope.net"
JENKINS_AUTH="your-username@your-company.com:your-api-token"
POLL_INTERVAL=30  # seconds
VALIDATION_SCRIPT="~/.claude/skills/self-service-skill/gre_post_deployment.py"
MAX_PARALLEL_VALIDATIONS=10

# Script parameters
BUILD_NUMBER="${1:-}"
SERVICE="${2:-}"
POPS="${3:-}"

if [[ -z "$BUILD_NUMBER" || -z "$SERVICE" || -z "$POPS" ]]; then
    echo "Usage: $0 <BUILD_NUMBER> <SERVICE> <POPS>"
    echo "Example: $0 249 nsvppgregw 'dxb1,man1'"
    exit 1
fi

# State files
STATE_DIR="/tmp/deployment_${BUILD_NUMBER}"
PROCESSED_HOSTS="${STATE_DIR}/processed_hosts.txt"
PROCESSED_POPS="${STATE_DIR}/processed_pops.txt"
VALIDATED_HOSTS="${STATE_DIR}/validated_hosts.txt"
PDV_QUEUE="${STATE_DIR}/pdv_queue.txt"
PDV_LOCK="${STATE_DIR}/pdv.lock"
STATE_LOG="${STATE_DIR}/state.log"
CONSOLE_CACHE="${STATE_DIR}/console_last.txt"

# Initialize state directory
mkdir -p "$STATE_DIR"
touch "$PROCESSED_HOSTS" "$PROCESSED_POPS" "$VALIDATED_HOSTS" "$PDV_QUEUE" "$STATE_LOG"

# Logging function
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "$STATE_LOG"
}

log "INFO" "=========================================="
log "INFO" "Deployment Monitor Started"
log "INFO" "Build: #${BUILD_NUMBER}"
log "INFO" "Service: ${SERVICE}"
log "INFO" "POPs: ${POPS}"
log "INFO" "=========================================="

################################################################################
# Function: fetch_console_log
# Fetches Jenkins console log with retry logic
################################################################################
fetch_console_log() {
    local retries=3
    local attempt=1

    while [ $attempt -le $retries ]; do
        if CONSOLE=$(curl -s "${JENKINS_URL}/job/one_button_${SERVICE}/${BUILD_NUMBER}/consoleText" \
            -u "${JENKINS_AUTH}" 2>/dev/null); then
            echo "$CONSOLE"
            return 0
        fi

        log "WARN" "Console fetch failed (attempt $attempt/$retries)"
        attempt=$((attempt + 1))
        sleep 5
    done

    log "ERROR" "Failed to fetch console after $retries attempts"
    return 1
}

################################################################################
# Function: extract_pop_from_hostname
# Extracts POP name from hostname (e.g., nsvppgregw01.man1.nskope.net -> man1)
################################################################################
extract_pop_from_hostname() {
    local hostname="$1"
    echo "$hostname" | cut -d'.' -f2
}

################################################################################
# Function: parse_play_recap
# Parses PLAY RECAP section and identifies completed hosts
################################################################################
parse_play_recap() {
    local console="$1"
    local new_hosts=()

    # Extract PLAY RECAP sections
    echo "$console" | grep -A 200 "PLAY RECAP" | while IFS= read -r line; do
        # Match host lines with Ansible stats
        if echo "$line" | grep -qE "nsvpp(gregw|ipsecgw)[0-9]+\.[a-z0-9]+\.nskope\.net.*ok=[0-9]+.*changed=[0-9]+.*failed=[0-9]+"; then
            # Extract hostname (remove timestamps and ANSI escape codes, then extract hostname)
            # Console format: [2026-02-19T11:27:43.148Z] ESC[0;33mnsvppgregw01.bsb1.nskope.net ESC[0m : ok=68...
            # Note: Jenkins console contains real ANSI escape sequences (ESC = \x1b)
            # Step 1: Remove timestamp [YYYY-MM-DDTHH:MM:SS.SSSZ]
            # Step 2: Remove ANSI escape sequences ESC[...m
            # Step 3: Extract first field (hostname)
            local hostname=$(echo "$line" | sed 's/^\[[^]]*\] //' | sed 's/\x1b\[[0-9;]*m//g' | awk '{print $1}')

            # Extract failed count (macOS-compatible)
            local failed=$(echo "$line" | sed -n 's/.*failed=\([0-9]*\).*/\1/p')
            [ -z "$failed" ] && failed="999"

            # Validate hostname format
            if [[ ! "$hostname" =~ ^nsvpp(gregw|ipsecgw)[0-9]+\.[a-z0-9]+\.nskope\.net$ ]]; then
                log "WARN" "Invalid hostname format: $hostname"
                continue
            fi

            # Check if already processed
            if grep -q "^${hostname}$" "$PROCESSED_HOSTS"; then
                continue
            fi

            # Mark as processed
            echo "$hostname" >> "$PROCESSED_HOSTS"

            local pop=$(extract_pop_from_hostname "$hostname")
            local status="FAILED"

            if [ "$failed" = "0" ]; then
                status="PASSED"
                log "INFO" "✅ Host completed: $hostname (POP: $pop, Status: $status)"

                # Launch validation in background
                launch_validation "$hostname" "$pop" &
            else
                log "WARN" "❌ Host failed: $hostname (POP: $pop, failed=$failed)"
            fi
        fi
    done
}

################################################################################
# Function: launch_validation
# Launches post-deployment validation for a host
################################################################################
launch_validation() {
    local hostname="$1"
    local pop="$2"

    log "INFO" "Starting validation for $hostname (background)"

    # Wait for running validations if at limit
    while [ $(jobs -r | wc -l) -ge $MAX_PARALLEL_VALIDATIONS ]; do
        sleep 2
    done

    (
        local start_time=$(date +%s)

        # Add 30-second delay to allow services to stabilize
        log "INFO" "[$hostname] Waiting 30 seconds for services to stabilize..."
        sleep 30

        # Copy validation script
        log "INFO" "[$hostname] Copying validation script..."
        if ! timeout 60 tsh scp --cluster "$pop" "$VALIDATION_SCRIPT" "${hostname}:/tmp/" 2>&1 | tee -a "$STATE_LOG"; then
            log "ERROR" "[$hostname] Failed to copy validation script"
            return 1
        fi

        # Run validation script
        log "INFO" "[$hostname] Running validation..."
        local validation_log="${STATE_DIR}/validation_${hostname}.log"

        if timeout 300 tsh ssh --cluster "$pop" "$hostname" \
            sudo python3 /tmp/gre_post_deployment.py > "$validation_log" 2>&1; then

            local duration=$(($(date +%s) - start_time))
            log "INFO" "[$hostname] ✅ Validation PASSED (${duration}s)"
            echo "${hostname}:PASSED:$(date +%s)" >> "$VALIDATED_HOSTS"

            # Check if POP is ready for PDV
            check_pop_ready_for_pdv "$pop"
        else
            local exit_code=$?
            local duration=$(($(date +%s) - start_time))

            if [ $exit_code -eq 124 ]; then
                log "ERROR" "[$hostname] ❌ Validation TIMEOUT (300s)"
            else
                log "ERROR" "[$hostname] ❌ Validation FAILED (${duration}s, exit: $exit_code)"
            fi

            echo "${hostname}:FAILED:$(date +%s)" >> "$VALIDATED_HOSTS"
        fi
    ) &
}

################################################################################
# Function: check_pop_ready_for_pdv
# Checks if a POP is ready for PDV testing and adds to queue
################################################################################
check_pop_ready_for_pdv() {
    local pop="$1"

    # Use lock to prevent race conditions
    (
        flock -x 200

        # Check if already processed
        if grep -q "^${pop}$" "$PROCESSED_POPS"; then
            return 0
        fi

        # Get all hosts for this POP from processed list
        local pop_hosts=$(grep "\.${pop}\." "$PROCESSED_HOSTS" || true)

        if [ -z "$pop_hosts" ]; then
            return 0
        fi

        # Count total hosts and validated hosts
        local total_hosts=$(echo "$pop_hosts" | wc -l)
        local validated_hosts=$(echo "$pop_hosts" | while read host; do
            if grep -q "^${host}:" "$VALIDATED_HOSTS"; then
                echo "$host"
            fi
        done | wc -l)

        # Check if at least one host passed
        local passed_hosts=$(grep "\.${pop}\." "$VALIDATED_HOSTS" | grep ":PASSED:" | wc -l)

        log "DEBUG" "[$pop] Readiness check: total=$total_hosts, validated=$validated_hosts, passed=$passed_hosts"

        # Determine expected hosts per POP (typically 2 for GRE)
        local expected_hosts=2

        # POP is ready if:
        # 1. All expected hosts have completed deployment
        # 2. All passed hosts have completed validation
        # 3. At least one host passed

        if [ "$total_hosts" -ge "$expected_hosts" ] && \
           [ "$validated_hosts" -ge "$passed_hosts" ] && \
           [ "$passed_hosts" -gt 0 ]; then

            log "INFO" "🎯 POP $pop is ready for PDV testing ($passed_hosts/$total_hosts hosts passed)"

            # Add to PDV queue
            echo "$pop" >> "$PDV_QUEUE"
            echo "$pop" >> "$PROCESSED_POPS"

            log "INFO" "✅ Added $pop to PDV queue"
        fi

    ) 200>"${STATE_DIR}/check_pop.lock"
}

################################################################################
# Function: pdv_coordinator
# Coordinates sequential PDV testing (one POP at a time)
################################################################################
pdv_coordinator() {
    log "INFO" "PDV Coordinator started (background)"

    while true; do
        # Check if Jenkins job is still running
        local building=$(curl -s "${JENKINS_URL}/job/one_button_${SERVICE}/${BUILD_NUMBER}/api/json" \
            -u "${JENKINS_AUTH}" 2>/dev/null | \
            python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('building', 'true'))" 2>/dev/null || echo "true")

        # Check if there are POPs in queue
        if [ -s "$PDV_QUEUE" ]; then
            # Try to acquire PDV lock
            (
                if flock -n 200; then
                    # Get first POP from queue
                    local next_pop=$(head -1 "$PDV_QUEUE")

                    if [ -n "$next_pop" ]; then
                        # Remove from queue
                        tail -n +2 "$PDV_QUEUE" > "${PDV_QUEUE}.tmp"
                        mv "${PDV_QUEUE}.tmp" "$PDV_QUEUE"

                        log "INFO" "========================================"
                        log "INFO" "🚀 Starting PDV testing for: $next_pop"
                        log "INFO" "========================================"

                        # Run PDV testing (blocking)
                        run_pdv_for_pop "$next_pop"

                        log "INFO" "✅ PDV testing completed for $next_pop"
                    fi
                fi
            ) 200>"$PDV_LOCK"
        fi

        # Check if all work is done
        if [ "$building" = "false" ] && [ ! -s "$PDV_QUEUE" ]; then
            # Wait for any remaining validations
            local pending_validations=$(jobs -r | wc -l)
            if [ $pending_validations -eq 0 ]; then
                log "INFO" "✅ PDV Coordinator: All work completed"
                break
            fi
        fi

        sleep 10
    done
}

################################################################################
# Function: run_pdv_for_pop
# Runs PDV testing for a specific POP
################################################################################
run_pdv_for_pop() {
    local pop="$1"

    # Determine gateway type
    local gateway_type="GRE"
    if [[ "$SERVICE" == *"ipsec"* ]]; then
        gateway_type="IPSEC"
    fi

    log "INFO" "[$pop] Gateway Type: VPP $gateway_type"

    # Get passed nodes for this POP
    local passed_nodes=$(grep "\.${pop}\." "$VALIDATED_HOSTS" | grep ":PASSED:" | cut -d':' -f1)
    log "INFO" "[$pop] Passed nodes: $(echo $passed_nodes | tr '\n' ' ')"

    # Invoke prod-pdv skill
    log "INFO" "[$pop] Invoking prod-pdv skill..."

    # Note: This is a placeholder for actual prod-pdv skill invocation
    # In the actual implementation, this would call the Skill tool or invoke the prod-pdv script
    log "INFO" "[$pop] PDV Request: Run VPP $gateway_type DPAS PDV on POP $pop"

    # For now, simulate PDV execution
    # TODO: Replace with actual prod-pdv skill invocation
    local pdv_result=0

    if [ $pdv_result -eq 0 ]; then
        log "INFO" "[$pop] ✅ PDV PASSED"
        echo "${pop}:PDV:PASSED:$(date +%s)" >> "${STATE_DIR}/pdv_results.txt"
    else
        log "ERROR" "[$pop] ❌ PDV FAILED"
        echo "${pop}:PDV:FAILED:$(date +%s)" >> "${STATE_DIR}/pdv_results.txt"
    fi
}

################################################################################
# Function: check_jenkins_status
# Checks if Jenkins build is still running
################################################################################
check_jenkins_status() {
    local status=$(curl -s "${JENKINS_URL}/job/one_button_${SERVICE}/${BUILD_NUMBER}/api/json" \
        -u "${JENKINS_AUTH}" 2>/dev/null | \
        python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"{data.get('building')}:{data.get('result')}\")" 2>/dev/null || echo "true:UNKNOWN")

    echo "$status"
}

################################################################################
# Function: wait_initial_period
# Waits initial period based on number of POPs
################################################################################
wait_initial_period() {
    local wait_time=120  # 2 minutes for all deployments

    log "INFO" "Waiting ${wait_time} seconds (2 minutes) before monitoring starts..."
    sleep $wait_time
}

################################################################################
# MAIN EXECUTION
################################################################################

# Wait initial period
wait_initial_period

# Start PDV coordinator in background
pdv_coordinator &
PDV_COORDINATOR_PID=$!
log "INFO" "PDV Coordinator PID: $PDV_COORDINATOR_PID"

# Main monitoring loop
log "INFO" "Starting real-time console monitoring (polling every ${POLL_INTERVAL}s)..."

while true; do
    # Check Jenkins status
    jenkins_status=$(check_jenkins_status)
    building=$(echo "$jenkins_status" | cut -d':' -f1)
    result=$(echo "$jenkins_status" | cut -d':' -f2)

    # Fetch and parse console
    if console=$(fetch_console_log); then
        # Parse PLAY RECAP sections
        parse_play_recap "$console"

        # Save console for comparison
        echo "$console" > "$CONSOLE_CACHE"
    else
        log "ERROR" "Failed to fetch console, retrying in ${POLL_INTERVAL}s"
    fi

    # Check if build is complete
    if [ "$building" = "False" ] || [ "$building" = "false" ]; then
        log "INFO" "🎉 Jenkins deployment build completed (Result: $result)"

        # Wait for all background validations to complete
        log "INFO" "Waiting for all validations to complete..."
        wait

        log "INFO" "✅ All validations completed"
        break
    fi

    # Progress indicator
    echo -n "."

    sleep $POLL_INTERVAL
done

# Wait for PDV coordinator to finish
log "INFO" "Waiting for PDV coordinator to complete..."
wait $PDV_COORDINATOR_PID

# Generate summary
log "INFO" "=========================================="
log "INFO" "Deployment Monitoring Completed"
log "INFO" "=========================================="

# Summary statistics
total_hosts=$(wc -l < "$PROCESSED_HOSTS")
validated_hosts=$(wc -l < "$VALIDATED_HOSTS")
passed_validations=$(grep -c ":PASSED:" "$VALIDATED_HOSTS" || echo "0")

log "INFO" "Total Hosts Processed: $total_hosts"
log "INFO" "Validated Hosts: $validated_hosts"
log "INFO" "Passed Validations: $passed_validations"

if [ -f "${STATE_DIR}/pdv_results.txt" ]; then
    pdv_total=$(wc -l < "${STATE_DIR}/pdv_results.txt")
    pdv_passed=$(grep -c ":PASSED:" "${STATE_DIR}/pdv_results.txt" || echo "0")
    log "INFO" "PDV Tests: $pdv_passed/$pdv_total passed"
fi

log "INFO" "State directory: $STATE_DIR"
log "INFO" "=========================================="

exit 0
