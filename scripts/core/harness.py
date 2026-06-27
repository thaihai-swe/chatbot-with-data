#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core._lib.yaml_reader import load as load_yaml


def resolve_root(root_flag):
    if root_flag:
        p = Path(root_flag).resolve()
        if (p / "AGENTS.md").exists() and (p / "memories/repo").exists():
            return p
        if (p / "kit/AGENTS.md").exists():
            return p / "kit"
    for d in [Path.cwd()] + list(Path.cwd().parents):
        if (d / "AGENTS.md").exists() and (d / "memories/repo").exists():
            return d
        if (d / "kit/AGENTS.md").exists():
            return d / "kit"
    sys.exit("ERROR: Could not resolve repository root")


class HarnessError(Exception):
    pass


class ConfigError(HarnessError):
    pass


class GateResult:
    def __init__(self, name, passed, output, error=None):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error


class Gate:
    def __init__(self, name, command, stack, on_fail, config):
        self.name = name
        self.command = command
        self.stack = stack
        self.on_fail = on_fail
        self.config = config

    def run(self, root_dir, dry_run=False):
        if dry_run:
            return GateResult(self.name, True, f"[dry-run] would run: {self.command}")
        try:
            result = subprocess.run(
                self.command, shell=True, capture_output=True, text=True,
                cwd=str(root_dir), timeout=self.config.get("thresholds", {}).get("timeout_seconds", 300)
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            return GateResult(self.name, passed, output, None if passed else output)
        except subprocess.TimeoutExpired as e:
            return GateResult(self.name, False, "", f"TIMEOUT: {e}")
        except Exception as e:
            return GateResult(self.name, False, "", str(e))


class Phase:
    def __init__(self, name, preconditions, config):
        self.name = name
        self.preconditions = preconditions
        self.config = config

    def check_preconditions(self, feature_dir, dry_run=False):
        fails = []
        for pc in self.preconditions:
            artifact = os.path.join(feature_dir, pc["artifact"])
            check = pc.get("check", "exists")
            if dry_run:
                continue
            if check == "exists":
                if not os.path.exists(artifact):
                    fails.append(f"Required artifact missing: {artifact}")
            elif check == "contains_stale":
                if os.path.exists(artifact):
                    with open(artifact) as f:
                        if "[STALE" in f.read():
                            fails.append(f"Artifact has STALE marker: {artifact}")
        return fails


class Lifecycle:
    def __init__(self, config):
        self.phases = [Phase(**p, config=config) for p in config.get("phases", [])]
        self.config = config

    def get_phase_names(self):
        return [p.name for p in self.phases]

    def _state_path(self, root, feature_slug):
        return Path(root) / "docs/generated/harness-state.json"

    def transition(self, current_phase_name, target_phase_name, feature_dir, dry_run=False, root=None):
        current_idx = -1
        target_idx = -1
        for i, p in enumerate(self.phases):
            if p.name == current_phase_name:
                current_idx = i
            if p.name == target_phase_name:
                target_idx = i
        if target_idx < 0:
            raise HarnessError(f"Unknown target phase: {target_phase_name}")
        if current_idx >= 0 and target_idx <= current_idx:
            raise HarnessError(
                f"Cannot transition from '{current_phase_name}' to '{target_phase_name}' — "
                f"phase must advance forward"
            )
        if target_idx > current_idx + 1:
            raise HarnessError(
                f"Cannot skip from '{current_phase_name}' to '{target_phase_name}' — "
                f"intermediate phases required"
            )

        feature_slug = Path(feature_dir).name
        if root:
            state_path = self._state_path(root, feature_slug)
        else:
            state_path = Path(feature_dir).parent.parent / "docs/generated/harness-state.json"
        state = self._load_state(state_path) if not dry_run else {}

        if target_phase_name == "Verifying" and state.get(feature_slug, {}).get("consecutive_gate_failures", 0) >= 2:
            raise HarnessError(
                f"CIRCUIT_BREAKER: 2 consecutive gate failures for '{feature_slug}'. "
                f"Return to /spec-plan and re-approve before retrying."
            )

        if target_phase_name == "Plan Approved" and state.get(feature_slug, {}):
            if not dry_run:
                state[feature_slug]["consecutive_gate_failures"] = 0
                state[feature_slug]["last_failure_at"] = None

        fails = self.phases[target_idx].check_preconditions(feature_dir, dry_run)
        if fails:
            raise HarnessError(f"Phase '{target_phase_name}' precondition failures:\n" +
                               "\n".join(fails))
        if not dry_run:
            Path(feature_dir).mkdir(parents=True, exist_ok=True)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            entry = state.get(feature_slug, {"consecutive_gate_failures": 0, "last_failure_at": None})
            entry["phase"] = target_phase_name
            state[feature_slug] = entry
            state_path.write_text(json.dumps(state, indent=2))
        return f"Transitioned to '{target_phase_name}'"

    def record_gate_failure(self, root, feature_slug, gate_name=""):
        state_path = self._state_path(root, feature_slug)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state = self._load_state(state_path)
        import datetime
        entry = state.get(feature_slug, {"phase": "", "consecutive_gate_failures": 0, "last_failure_at": None})
        entry["consecutive_gate_failures"] = entry.get("consecutive_gate_failures", 0) + 1
        entry["last_failure_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entry["last_failed_gate"] = gate_name
        state[feature_slug] = entry
        state_path.write_text(json.dumps(state, indent=2))
        return entry["consecutive_gate_failures"]

    def record_gate_success(self, root, feature_slug):
        state_path = self._state_path(root, feature_slug)
        if not state_path.exists():
            return 0
        state = self._load_state(state_path)
        entry = state.get(feature_slug, {})
        if "consecutive_gate_failures" in entry:
            entry["consecutive_gate_failures"] = 0
        state[feature_slug] = entry
        state_path.write_text(json.dumps(state, indent=2))
        return 0

    def _load_state(self, path):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except (json.JSONDecodeError, Exception):
                pass
        return {}

    def get_state(self, feature_slug, root=None):
        if root:
            state_path = Path(root) / "docs/generated/harness-state.json"
        else:
            state_path = Path(feature_slug).parent.parent / "docs/generated/harness-state.json"
        state = self._load_state(state_path)
        return state.get(feature_slug, {})


class HarnessConfig:
    def __init__(self, config_path):
        self.path = Path(config_path)
        if not self.path.exists():
            raise ConfigError(f"Config not found: {config_path}")
        self.data = load_yaml(self.path)
        self.validate()

    def validate(self):
        if "phases" not in self.data:
            raise ConfigError("harness-config.yaml must contain 'phases' key")
        for p in self.data["phases"]:
            if "name" not in p:
                raise ConfigError("Each phase must have a 'name'")
        if "gates" not in self.data:
            self.data["gates"] = []

    def get_gates_for_stack(self, stack_name):
        if not stack_name:
            return [Gate(**g, config=self.data) for g in self.data.get("gates", [])]
        detection = self.data.get("stack_detection", {})
        for name, cfg in detection.items():
            if stack_name == name:
                gate_names = set(cfg.get("gates", []))
                return [Gate(**g, config=self.data) for g in self.data.get("gates", [])
                        if g["name"] in gate_names]
        return []

    def detect_stack(self, root_dir):
        explicit = self.data.get("stack", "auto")
        if explicit != "auto":
            return explicit
        root = Path(root_dir)
        detection = self.data.get("stack_detection", {})
        found = []
        for name, cfg in detection.items():
            for f in cfg.get("files", []):
                if (root / f).exists():
                    found.append(name)
                    break
        if len(found) > 1:
            print(f"WARN: multiple stack markers detected ({', '.join(found)}); "
                  f"using '{found[0]}'. Set 'stack:' in harness-config.yaml to override.",
                  file=sys.stderr)
        return found[0] if found else None

    def get_preflight_checks(self, stack_name):
        preflight = self.data.get("preflight_tools", {})
        all_checks = []
        for name, cfg in preflight.items():
            stack_filter = cfg.get("stack", None)
            if stack_filter and stack_filter != stack_name:
                continue
            all_checks.append((name, cfg.get("command"), cfg.get("optional", False)))
        return all_checks


def cmd_gates(args):
    root = resolve_root(args.root)
    config = HarnessConfig(args.config or root / "docs/project/harness-config.yaml")
    if not args.stack:
        args.stack = config.detect_stack(root) or ""
    gates = config.get_gates_for_stack(args.stack)
    if not gates:
        print(f"ERROR: No gates defined for stack '{args.stack}'", file=sys.stderr)
        sys.exit(1)
    preflight = config.get_preflight_checks(args.stack)
    for name, cmd, optional in preflight:
        if args.dry_run:
            print(f"[dry-run] would check preflight: {name} ({cmd})")
        elif not optional:
            if not shutil.which(cmd):
                print(f"SETUP_FAILURE: Required tool '{cmd}' not found", file=sys.stderr)
                sys.exit(2)
    for gate in gates:
        if args.dry_run:
            print(f"[dry-run] would run gate: {gate.name} → {gate.command}")
        else:
            result = gate.run(root)
            if not result.passed:
                print(result.output)
                print(f"=> Gate failed: {gate.name}", file=sys.stderr)
                sys.exit(1)
    print("=> All gates passed successfully.")


def cmd_phase_gate(args):
    root = resolve_root(args.root)
    config = HarnessConfig(args.config or root / "docs/project/harness-config.yaml")
    lifecycle = Lifecycle(config.data)
    try:
        if args.phase == "Verifying":
            state_path = root / "docs/generated/harness-state.json"
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            entry = state.get(args.feature, {})
            failures = entry.get("consecutive_gate_failures", 0)
            if failures >= 2:
                print(f"FAIL: CIRCUIT_BREAKER — {failures} consecutive gate failures for "
                      f"'{args.feature}'. Return to /spec-plan and re-approve before retrying.",
                      file=sys.stderr)
                sys.exit(1)
        fails = []
        for p in lifecycle.phases:
            if p.name == args.phase:
                fails = p.check_preconditions(
                    root / f"artifacts/features/{args.feature}",
                    args.dry_run
                )
                break
        else:
            print(f"PASS: no specific preconditions for phase '{args.phase}'")
            return
        if fails:
            for f in fails:
                print(f"FAIL: {f}")
            sys.exit(1)
        print(f"PASS: all preconditions met for '{args.phase}'")
    except HarnessError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle(args):
    root = resolve_root(args.root)
    config = HarnessConfig(args.config or root / "docs/project/harness-config.yaml")
    lifecycle = Lifecycle(config.data)
    try:
        if args.action == "transition":
            feature_dir = root / f"artifacts/features/{args.feature}"
            msg = lifecycle.transition(
                args.current_phase or "", args.phase, feature_dir, args.dry_run, root=root
            )
            print(msg)
        elif args.action == "state":
            state_path = root / "docs/generated/harness-state.json"
            if state_path.exists():
                print(state_path.read_text())
            else:
                print("{}")
        elif args.action == "record-failure":
            if not args.feature:
                print("ERROR: --feature required for record-failure", file=sys.stderr)
                sys.exit(1)
            count = lifecycle.record_gate_failure(root, args.feature, args.gate)
            print(f"Gate failure recorded ({count} consecutive)")
        elif args.action == "record-success":
            if not args.feature:
                print("ERROR: --feature required for record-success", file=sys.stderr)
                sys.exit(1)
            lifecycle.record_gate_success(root, args.feature)
            print("Gate success recorded (failures reset)")
        else:
            print(f"Unknown lifecycle action: {args.action}", file=sys.stderr)
            sys.exit(1)
    except HarnessError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_config_validate(args):
    root = resolve_root(args.root)
    config = HarnessConfig(args.config or root / "docs/project/harness-config.yaml")
    print(f"Config validates OK: {len(config.data.get('phases', []))} phases, "
          f"{len(config.data.get('gates', []))} gates")


def main():
    parser = argparse.ArgumentParser(description="CoreZero Harness Engine")
    parser.add_argument("--root", default="", help="Repository root directory")
    parser.add_argument("--config", default="", help="Path to harness-config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")

    sub = parser.add_subparsers(dest="mode", required=True)

    gates_p = sub.add_parser("gates", help="Run mechanical gates")
    gates_p.add_argument("--stack", default="", help="Stack name (node, python, auto)")
    gates_p.set_defaults(func=cmd_gates)

    pg_p = sub.add_parser("phase-gate", help="Check phase preconditions")
    pg_p.add_argument("--phase", required=True, help="Target phase name")
    pg_p.add_argument("--feature", required=True, help="Feature slug")
    pg_p.set_defaults(func=cmd_phase_gate)

    lc_p = sub.add_parser("lifecycle", help="Lifecycle state machine")
    lc_p.add_argument("--action", required=True, choices=["transition", "state", "record-failure", "record-success"])
    lc_p.add_argument("--phase", default="", help="Target phase name")
    lc_p.add_argument("--feature", default="", help="Feature slug")
    lc_p.add_argument("--current-phase", default="", help="Current phase name")
    lc_p.add_argument("--gate", default="", help="Gate name (for record-failure)")
    lc_p.set_defaults(func=cmd_lifecycle)

    cv_p = sub.add_parser("config-validate", help="Validate harness config")
    cv_p.set_defaults(func=cmd_config_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
