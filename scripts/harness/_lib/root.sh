#!/usr/bin/env bash
# _lib/root.sh
# Sourced by harness scripts to resolve the repository root directory.

resolve_repo_root() {
  local root_dir="${1:-}"
  
  if [[ -n "$root_dir" ]]; then
    if [[ -f "$root_dir/AGENTS.md" && -d "$root_dir/core-zero/memories/repo" ]]; then
      echo "$root_dir"
      return 0
    fi
    if [[ -d "$root_dir/kit" && -f "$root_dir/kit/AGENTS.md" ]]; then
      echo "$root_dir/kit"
      return 0
    fi
  fi
  
  # Walk upward from current directory
  local current_dir="$PWD"
  while [[ "$current_dir" != "/" && -n "$current_dir" ]]; do
    if [[ -f "$current_dir/AGENTS.md" && -d "$current_dir/core-zero/memories/repo" ]]; then
      echo "$current_dir"
      return 0
    fi
    if [[ -d "$current_dir/kit" && -f "$current_dir/kit/AGENTS.md" ]]; then
      echo "$current_dir/kit"
      return 0
    fi
    local parent_dir
    parent_dir="$(dirname "$current_dir")"
    if [[ "$parent_dir" == "$current_dir" ]]; then
      break
    fi
    current_dir="$parent_dir"
  done
  
  # Fallback to local check
  if [[ -f "$PWD/AGENTS.md" && -d "$PWD/core-zero/memories/repo" ]]; then
    echo "$PWD"
    return 0
  fi
  
  return 1
}
