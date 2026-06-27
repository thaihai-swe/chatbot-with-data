#!/usr/bin/env bash
# gate-runner.local.example.sh
# Generic template for project-local gate overrides.
# Copy to gate-runner.local.sh and customize with your build/lint/test commands.
#   cp scripts/harness/gate-runner.local.example.sh scripts/harness/gate-runner.local.sh

# Helper function to run a gate command, log output, and report failures to telemetry
run_gate() {
  local cmd="$1"
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local telemetry_script="$script_dir/telemetry-collector.sh"
  
  echo "=> Running: $cmd"
  if ! OUTPUT=$(eval "$cmd" 2>&1); then
    echo "$OUTPUT"
    echo "=> Gate failed: $cmd"
    if [ -x "$telemetry_script" ]; then
      echo "$OUTPUT" | "$telemetry_script"
    fi
    exit 1
  fi
}

echo "=> Running project-local gates..."

# Uncomment and customize the commands for your stack:
# run_gate "npm run lint"
# run_gate "npm run typecheck"
# run_gate "npm test"
# run_gate "go build ./... && go vet ./..."
# run_gate "cargo build && cargo clippy"
# run_gate "mvn test"
# run_gate "bundle exec rake test"
# run_gate "pytest"
# run_gate "dotnet test"

echo "=> All project-local gates passed."
exit 0
