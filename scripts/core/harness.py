#!/usr/bin/env python3
import argparse
import fcntl
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core._lib.root import resolve_root
from core._lib.yaml_reader import load as load_yaml


class HarnessError(Exception):
    pass


class ConfigError(HarnessError):
    pass


class GateResult:
    def __init__(self, name, passed, output, error=None, duration_ms=0):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self):
        output_tail = self.output[-2000:] if self.output else ""
        return {
            "name": self.name,
            "passed": self.passed,
            "output": self.output,
            "output_tail": output_tail,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class Gate:
    def __init__(self, name, command, stack, on_fail, config):
        self.name = name
        self.command = command
        self.stack = stack
        self.on_fail = on_fail or "block"
        self.config = config

    def run(self, root_dir, dry_run=False):
        import time
        if dry_run:
            return GateResult(self.name, True, f"[dry-run] would run: {self.command}", duration_ms=0)
        start_time = time.time()
        try:
            # ponytail: shell=True; split argv when gate commands are simple binaries only
            result = subprocess.run(
                self.command, shell=True, capture_output=True, text=True,
                cwd=str(root_dir), timeout=self.config.get("thresholds", {}).get("timeout_seconds", 300)
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            duration_ms = int((time.time() - start_time) * 1000)
            return GateResult(self.name, passed, output, None if passed else output, duration_ms)
        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return GateResult(self.name, False, "", f"TIMEOUT: {e}", duration_ms)
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return GateResult(self.name, False, "", str(e), duration_ms)



def resolve_artifact_path(feature_dir, artifact_template, feature_slug=None):
    """Resolve precondition artifact path.

    - Substitute <slug> and {feature} with feature_slug.
    - Paths starting with features/ resolve from artifacts/ (parent of feature_dir's parent).
    - Otherwise paths are relative to feature_dir.
    """
    slug = feature_slug or Path(feature_dir).name
    artifact = (
        str(artifact_template)
        .replace("<slug>", slug)
        .replace("{feature}", slug)
    )
    if artifact.startswith("features/") or artifact.startswith("features\\"):
        artifacts_root = Path(feature_dir).parent.parent
        return str(artifacts_root / artifact)
    return os.path.join(feature_dir, artifact)


class Phase:
    def __init__(self, name, preconditions, config):
        self.name = name
        self.preconditions = preconditions
        self.config = config

    def check_preconditions(self, feature_dir, dry_run=False, feature_slug=None):
        fails = []
        slug = feature_slug or Path(feature_dir).name
        for pc in self.preconditions:
            artifact = resolve_artifact_path(feature_dir, pc["artifact"], slug)
            check = pc.get("check", "exists")
            if dry_run:
                continue
            if check == "exists":
                if not os.path.exists(artifact):
                    fails.append(f"Required artifact missing: {artifact}")
            elif check == "contains_stale":
                if os.path.exists(artifact):
                    with open(artifact) as f:
                        if "[:HALT" in f.read():
                            fails.append(f"Artifact has [:HALT marker: {artifact}")
        return fails


class Lifecycle:
    def __init__(self, config):
        self.phases = [Phase(**p, config=config) for p in config.get("phases", [])]
        self.config = config

    def get_phase_names(self):
        return [p.name for p in self.phases]

    def circuit_breaker_config(self):
        """Return (block_phase, reset_phase, max_failures) from config.

        block_phase defaults to last configured phase (not a magic string).
        reset_phase defaults to None unless set in circuit_breaker.reset_phase.
        """
        cb = self.config.get("circuit_breaker") or {}
        names = self.get_phase_names()
        block = cb.get("block_phase") or (names[-1] if names else None)
        reset = cb.get("reset_phase")
        max_failures = int(cb.get("max_failures", 2))
        return block, reset, max_failures

    def _state_path(self, root):
        return Path(root) / "core-zero/generated/harness-state.json"

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
            state_path = self._state_path(root)
        else:
            state_path = self._state_path(Path(feature_dir).parent.parent)

        fails = self.phases[target_idx].check_preconditions(
            feature_dir, dry_run, feature_slug=feature_slug
        )
        if fails:
            raise HarnessError(f"Phase '{target_phase_name}' precondition failures:\n" +
                               "\n".join(fails))

        if dry_run:
            return f"Transitioned to '{target_phase_name}'"

        Path(feature_dir).mkdir(parents=True, exist_ok=True)
        block_phase, reset_phase, max_failures = self.circuit_breaker_config()

        def mutator(state):
            entry = state.get(feature_slug, {"consecutive_gate_failures": 0, "last_failure_at": None})
            if (
                block_phase
                and target_phase_name == block_phase
                and entry.get("consecutive_gate_failures", 0) >= max_failures
            ):
                raise HarnessError(
                    f"CIRCUIT_BREAKER: {max_failures} consecutive gate failures for '{feature_slug}'. "
                    f"Return to /spec-plan and re-approve before retrying."
                )
            if reset_phase and target_phase_name == reset_phase:
                entry["consecutive_gate_failures"] = 0
                entry["last_failure_at"] = None
            entry["phase"] = target_phase_name
            state[feature_slug] = entry
            return None

        self._mutate_state(state_path, mutator)
        return f"Transitioned to '{target_phase_name}'"

    def record_gate_failure(self, root, feature_slug, gate_name=""):
        import datetime
        state_path = self._state_path(root)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        def mutator(state):
            entry = state.get(feature_slug, {"phase": "", "consecutive_gate_failures": 0, "last_failure_at": None})
            entry["consecutive_gate_failures"] = entry.get("consecutive_gate_failures", 0) + 1
            entry["last_failure_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            entry["last_failed_gate"] = gate_name
            state[feature_slug] = entry
            return entry["consecutive_gate_failures"]

        return self._mutate_state(state_path, mutator)

    def record_gate_success(self, root, feature_slug):
        state_path = self._state_path(root)
        if not state_path.exists():
            return 0

        def mutator(state):
            entry = state.get(feature_slug, {})
            if "consecutive_gate_failures" in entry:
                entry["consecutive_gate_failures"] = 0
            state[feature_slug] = entry
            return 0

        return self._mutate_state(state_path, mutator)

    def list_features(self, root):
        """Return list of {slug, phase, consecutive_gate_failures, last_failure_at, last_failed_gate}."""
        state = self._load_state(self._state_path(root))
        rows = []
        for slug, entry in sorted(state.items()):
            if not isinstance(entry, dict):
                continue
            rows.append({
                "slug": slug,
                "phase": entry.get("phase", ""),
                "consecutive_gate_failures": entry.get("consecutive_gate_failures", 0),
                "last_failure_at": entry.get("last_failure_at"),
                "last_failed_gate": entry.get("last_failed_gate", ""),
            })
        return rows

    def _load_state(self, path):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                print("WARN: corrupt harness-state.json, resetting to default", file=sys.stderr)
            except Exception:
                raise ConfigError("Unexpected error reading harness-state.json")
        return {}

    def _mutate_state(self, state_path, mutator):
        """Load-modify-write harness-state.json under exclusive flock."""
        state_path = Path(state_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        if not state_path.exists():
            state_path.write_text("{}")
        with open(state_path, "r+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                try:
                    raw = f.read()
                    state = json.loads(raw) if raw.strip() else {}
                except json.JSONDecodeError:
                    print("WARN: corrupt harness-state.json, resetting to default", file=sys.stderr)
                    state = {}
                result = mutator(state)
                tmp = tempfile.NamedTemporaryFile(
                    mode="w", dir=str(state_path.parent),
                    prefix=".harness-state-", suffix=".tmp", delete=False,
                )
                try:
                    tmp.write(json.dumps(state, indent=2))
                    tmp.close()
                    os.replace(tmp.name, state_path)
                except Exception:
                    try:
                        os.unlink(tmp.name)
                    except OSError:
                        pass
                    raise
                return result
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def get_state(self, feature_slug, root=None):
        if root:
            state_path = Path(root) / "core-zero/generated/harness-state.json"
        else:
            state_path = Path(feature_slug).parent.parent / "core-zero/generated/harness-state.json"
        state = self._load_state(state_path)
        return state.get(feature_slug, {})


_VALID_ON_FAIL = {"block", "warn", "continue"}


class HarnessConfig:
    def __init__(self, config_path):
        self.path = Path(config_path)
        if not self.path.exists():
            raise ConfigError(f"Config not found: {config_path}")
        self.data = load_yaml(self.path)
        self.validate()

    def _default_on_fail(self):
        defaults = self.data.get("gate_defaults") or {}
        val = defaults.get("on_fail", "block")
        return val if val in _VALID_ON_FAIL else "block"

    def _make_gate(self, g):
        on_fail = g.get("on_fail") or self._default_on_fail()
        return Gate(
            name=g["name"],
            command=g["command"],
            stack=g.get("stack", ""),
            on_fail=on_fail,
            config=self.data,
        )

    def validate(self):
        if "phases" not in self.data:
            raise ConfigError("harness-config.yaml must contain 'phases' key")
        for p in self.data["phases"]:
            if "name" not in p:
                raise ConfigError("Each phase must have a 'name'")
        if "gates" not in self.data:
            self.data["gates"] = []

        detection = self.data.get("stack_detection") or {}
        gate_names = {g.get("name") for g in self.data.get("gates", []) if isinstance(g, dict)}

        for g in self.data.get("gates", []):
            if not isinstance(g, dict):
                continue
            stack = g.get("stack") or ""
            if stack and stack not in detection:
                raise ConfigError(
                    f"Gate '{g.get('name')}' stack '{stack}' not in stack_detection"
                )
            on_fail = g.get("on_fail")
            if on_fail is not None and on_fail not in _VALID_ON_FAIL:
                raise ConfigError(
                    f"Gate '{g.get('name')}' on_fail '{on_fail}' invalid "
                    f"(use block|warn|continue)"
                )

        for name, cfg in detection.items():
            if not isinstance(cfg, dict):
                continue
            for gn in cfg.get("gates", []) or []:
                if gn not in gate_names:
                    raise ConfigError(
                        f"stack_detection.{name}.gates references unknown gate '{gn}'"
                    )

        defaults = self.data.get("gate_defaults") or {}
        d_on = defaults.get("on_fail")
        if d_on is not None and d_on not in _VALID_ON_FAIL:
            raise ConfigError(
                f"gate_defaults.on_fail '{d_on}' invalid (use block|warn|continue)"
            )

        th = self.data.get("thresholds") or {}
        for key in (
            "token_warn", "token_hard", "timeout_seconds",
            "memory_warn_lines", "memory_breach_lines", "memory_hard_lines",
        ):
            if key in th:
                try:
                    val = int(th[key])
                except (TypeError, ValueError):
                    raise ConfigError(f"thresholds.{key} must be an integer")
                if val <= 0:
                    raise ConfigError(f"thresholds.{key} must be positive")

        if "token_warn" in th and "token_hard" in th:
            if int(th["token_warn"]) >= int(th["token_hard"]):
                raise ConfigError("thresholds.token_warn must be < token_hard")

        mem_keys = ("memory_warn_lines", "memory_breach_lines", "memory_hard_lines")
        if all(k in th for k in mem_keys):
            w, b, h = int(th[mem_keys[0]]), int(th[mem_keys[1]]), int(th[mem_keys[2]])
            if not (w < b < h):
                raise ConfigError(
                    "thresholds memory ladder must be warn < breach < hard"
                )

        cb = self.data.get("circuit_breaker") or {}
        phase_names = {p.get("name") for p in self.data.get("phases", [])}
        for key in ("block_phase", "reset_phase"):
            val = cb.get(key)
            if val and val not in phase_names:
                print(
                    f"WARN: circuit_breaker.{key} '{val}' not in phase names",
                    file=sys.stderr,
                )

    def get_gates_for_stack(self, stack_name):
        if not stack_name:
            return [self._make_gate(g) for g in self.data.get("gates", [])]
        detection = self.data.get("stack_detection", {})
        for name, cfg in detection.items():
            if stack_name == name:
                gate_names = set(cfg.get("gates", []))
                return [
                    self._make_gate(g) for g in self.data.get("gates", [])
                    if g["name"] in gate_names
                ]
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


def _emit(args, payload, text):
    """Print JSON payload when --json, else human text."""
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
    else:
        print(text)


def _read_version(root):
    """Read version from manifest.json under root (or kit/manifest.json)."""
    candidates = [
        Path(root) / "manifest.json",
        Path(root) / "kit" / "manifest.json",
        _SCRIPT_DIR.parent.parent / "manifest.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                return json.loads(p.read_text()).get("version", "unknown")
            except (json.JSONDecodeError, OSError):
                continue
    return "unknown"


def cmd_gates(args):
    try:
        root = Path(resolve_root(args.root) or args.root or Path.cwd())
        config = HarnessConfig(args.config or str(Path(root) / "core-zero/project/harness-config.yaml"))
        if not args.stack:
            args.stack = config.detect_stack(root) or ""
        gates = config.get_gates_for_stack(args.stack)
        if not gates:
            msg = f"ERROR: No gates defined for stack '{args.stack}'"
            if getattr(args, "json", False):
                print(json.dumps({"error": msg, "all_passed": False}))
            else:
                print(msg, file=sys.stderr)
            sys.exit(1)
        preflight = config.get_preflight_checks(args.stack)
        for name, cmd, optional in preflight:
            if args.dry_run:
                print(f"[dry-run] would check preflight: {name} ({cmd})")
            elif not optional:
                if not shutil.which(shlex.split(cmd)[0]):
                    print(f"SETUP_FAILURE: Required tool '{cmd}' not found", file=sys.stderr)
                    sys.exit(2)

        results = []
        all_passed = True
        for gate in gates:
            if args.dry_run:
                print(f"[dry-run] would run gate: {gate.name} → {gate.command}")
                results.append({"name": gate.name, "passed": True, "output": "[dry-run]", "error": None, "duration_ms": 0, "output_tail": "[dry-run]"})
                continue
            result = gate.run(root)
            results.append(result.to_dict())
            if not result.passed:
                all_passed = False
                if not getattr(args, "json", False):
                    print(result.output)
                    print(f"=> Gate failed: {gate.name}", file=sys.stderr)
                # Write report before exit/warn
                if getattr(args, "report", None):
                    import datetime
                    report_path = Path(args.report)
                    report_path.parent.mkdir(parents=True, exist_ok=True)
                    report_data = {
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "stack": args.stack,
                        "results": results,
                        "all_passed": all_passed,
                    }
                    report_path.write_text(json.dumps(report_data, indent=2))
                if gate.on_fail == "warn":
                    if not getattr(args, "json", False):
                        print(f"  (on_fail=warn, continuing)", file=sys.stderr)
                    continue
                elif gate.on_fail == "continue":
                    continue
                # block (default)
                if getattr(args, "json", False):
                    print(json.dumps({"results": results, "all_passed": False}))
                sys.exit(1)

        if getattr(args, "report", None):
            import datetime
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_data = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "stack": args.stack,
                "results": results,
                "all_passed": all_passed,
            }
            report_path.write_text(json.dumps(report_data, indent=2))

        if getattr(args, "json", False):
            print(json.dumps({"results": results, "all_passed": all_passed}))
        else:
            print("=> All gates passed successfully.")
    except (HarnessError, ConfigError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_phase_gate(args):
    root = Path(resolve_root(args.root) or args.root or Path.cwd())
    config = HarnessConfig(args.config or str(Path(root) / "core-zero/project/harness-config.yaml"))
    lifecycle = Lifecycle(config.data)
    try:
        # Circuit breaker check: if we are trying to enter the block_phase and have too many failures, fail.
        block_phase, _, max_failures = lifecycle.circuit_breaker_config()
        if block_phase and args.phase == block_phase:
            feature_slug = args.feature
            state_path = root / "core-zero/generated/harness-state.json"
            if state_path.exists():
                state = json.loads(state_path.read_text())
                entry = state.get(feature_slug, {})
                failures = entry.get("consecutive_gate_failures", 0)
                if failures >= max_failures:
                    msg = (
                        f"FAIL: CIRCUIT_BREAKER — {failures} consecutive gate failures for "
                        f"'{feature_slug}'. Return to /spec-plan and re-approve before retrying."
                    )
                    if getattr(args, "json", False):
                        print(json.dumps({
                            "phase": args.phase, "feature": args.feature,
                            "passed": False, "fails": [msg],
                        }))
                    else:
                        print(msg, file=sys.stderr)
                    sys.exit(1)

        fails = []
        for p in lifecycle.phases:
            if p.name == args.phase:
                fails = p.check_preconditions(
                    root / f"artifacts/features/{args.feature}",
                    args.dry_run,
                    feature_slug=args.feature
                )
                break
        else:
            payload = {
                "phase": args.phase, "feature": args.feature,
                "passed": True, "fails": [],
            }
            _emit(args, payload, f"PASS: no specific preconditions for phase '{args.phase}'")
            return
        if fails:
            payload = {
                "phase": args.phase, "feature": args.feature,
                "passed": False, "fails": fails,
            }
            if getattr(args, "json", False):
                print(json.dumps(payload, indent=2))
            else:
                for f in fails:
                    print(f"FAIL: {f}")
            sys.exit(1)
        payload = {
            "phase": args.phase, "feature": args.feature,
            "passed": True, "fails": [],
        }
        _emit(args, payload, f"PASS: all preconditions met for '{args.phase}'")
    except HarnessError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle(args):
    root = Path(resolve_root(args.root) or args.root or Path.cwd())
    config = HarnessConfig(args.config or str(Path(root) / "core-zero/project/harness-config.yaml"))
    lifecycle = Lifecycle(config.data)
    try:
        if args.action == "transition":
            feature_dir = root / f"artifacts/features/{args.feature}"
            msg = lifecycle.transition(
                args.current_phase or "", args.phase, feature_dir, args.dry_run, root=root
            )
            _emit(args, {"action": "transition", "message": msg, "feature": args.feature,
                         "phase": args.phase}, msg)
        elif args.action == "state":
            state_path = root / "core-zero/generated/harness-state.json"
            if state_path.exists():
                raw = state_path.read_text()
                if getattr(args, "json", False):
                    try:
                        print(json.dumps(json.loads(raw), indent=2))
                    except json.JSONDecodeError:
                        print("{}")
                else:
                    print(raw)
            else:
                print("{}" if getattr(args, "json", False) else "{}")
        elif args.action == "list":
            rows = lifecycle.list_features(root)
            if getattr(args, "json", False):
                print(json.dumps(rows, indent=2))
            else:
                if not rows:
                    print("(no features in harness-state.json)")
                else:
                    for r in rows:
                        print(
                            f"{r['slug']}\tphase={r['phase'] or '—'}\t"
                            f"failures={r['consecutive_gate_failures']}\t"
                            f"last_fail={r['last_failure_at'] or '—'}\t"
                            f"gate={r['last_failed_gate'] or '—'}"
                        )
        elif args.action == "record-failure":
            if not args.feature:
                print("ERROR: --feature required for record-failure", file=sys.stderr)
                sys.exit(1)
            count = lifecycle.record_gate_failure(root, args.feature, args.gate)
            msg = f"Gate failure recorded ({count} consecutive)"
            _emit(args, {"action": "record-failure", "feature": args.feature,
                         "count": count}, msg)
        elif args.action == "record-success":
            if not args.feature:
                print("ERROR: --feature required for record-success", file=sys.stderr)
                sys.exit(1)
            lifecycle.record_gate_success(root, args.feature)
            msg = "Gate success recorded (failures reset)"
            _emit(args, {"action": "record-success", "feature": args.feature}, msg)
        elif args.action == "reset":
            if not args.feature:
                print("ERROR: --feature required for reset", file=sys.stderr)
                sys.exit(1)
            lifecycle.record_gate_success(root, args.feature)
            msg = f"Circuit breaker reset for '{args.feature}'"
            _emit(args, {"action": "reset", "feature": args.feature}, msg)
        else:
            print(f"Unknown lifecycle action: {args.action}", file=sys.stderr)
            sys.exit(1)
    except HarnessError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_config_validate(args):
    try:
        root = Path(resolve_root(args.root) or args.root or Path.cwd())
        config = HarnessConfig(args.config or str(Path(root) / "core-zero/project/harness-config.yaml"))
        n_phases = len(config.data.get("phases", []))
        n_gates = len(config.data.get("gates", []))
        payload = {"ok": True, "phases": n_phases, "gates": n_gates}
        _emit(args, payload, f"Config validates OK: {n_phases} phases, {n_gates} gates")
    except (HarnessError, ConfigError) as e:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_doctor(args):
    """Run pure-Python doctor checks from doctor_checks.py."""
    try:
        from core._lib import doctor_checks
    except ImportError:
        from core._lib import doctor_checks  # type: ignore

    root = resolve_root(args.root)
    if not root:
        print("ERROR: could not resolve repo root", file=sys.stderr)
        sys.exit(2)

    checks = []
    failed = 0

    # thresholds readable
    try:
        ew, tb, hc = doctor_checks.read_thresholds(str(root))
        checks.append({
            "name": "thresholds",
            "status": "pass",
            "message": f"memory thresholds {ew}/{tb}/{hc}",
        })
    except Exception as e:
        checks.append({"name": "thresholds", "status": "fail", "message": str(e)})
        failed += 1

    # path map non-empty if core-zero exists
    try:
        pm = doctor_checks.build_path_map(str(root))
        checks.append({
            "name": "path_map",
            "status": "pass",
            "message": f"{len(pm)} memory/rule paths indexed",
        })
    except Exception as e:
        checks.append({"name": "path_map", "status": "fail", "message": str(e)})
        failed += 1

    # manifest drift
    try:
        result = doctor_checks.check_manifest_drift(str(root))
        status = "pass" if result == "OK" else ("skip" if result == "SKIP" else "fail")
        if status == "fail":
            failed += 1
        checks.append({"name": "manifest_drift", "status": status, "message": result})
    except Exception as e:
        checks.append({"name": "manifest_drift", "status": "fail", "message": str(e)})
        failed += 1

    payload = {"checks": checks, "failed": failed}
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
    else:
        for c in checks:
            mark = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}.get(c["status"], c["status"])
            print(f"  [{mark}] {c['name']}: {c['message']}")
        if failed:
            print(f"{failed} check(s) failed.")
        else:
            print("All Python doctor checks passed.")
    sys.exit(1 if failed else 0)


def main():
    parser = argparse.ArgumentParser(description="CoreZero Harness Engine")
    parser.add_argument("--root", default="", help="Repository root directory")
    parser.add_argument("--config", default="", help="Path to harness-config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--version", action="store_true",
        help="Print kit version from manifest.json and exit",
    )

    sub = parser.add_subparsers(dest="mode", required=False)

    gates_p = sub.add_parser("gates", help="Run mechanical gates")
    gates_p.add_argument("--stack", default="", help="Stack name (node, python, auto)")
    gates_p.add_argument("--report", default="", help="Path to write structured JSON report")
    gates_p.set_defaults(func=cmd_gates)

    pg_p = sub.add_parser("phase-gate", help="Check phase preconditions")
    pg_p.add_argument("--phase", required=True, help="Target phase name")
    pg_p.add_argument("--feature", required=True, help="Feature slug")
    pg_p.set_defaults(func=cmd_phase_gate)

    lc_p = sub.add_parser("lifecycle", help="Lifecycle state machine")
    lc_p.add_argument(
        "--action", required=True,
        choices=["transition", "state", "list", "record-failure", "record-success", "reset"],
    )
    lc_p.add_argument("--phase", default="", help="Target phase name")
    lc_p.add_argument("--feature", default="", help="Feature slug")
    lc_p.add_argument("--current-phase", default="", help="Current phase name")
    lc_p.add_argument("--gate", default="", help="Gate name (for record-failure)")
    lc_p.set_defaults(func=cmd_lifecycle)

    cv_p = sub.add_parser("config-validate", help="Validate harness config")
    cv_p.set_defaults(func=cmd_config_validate)

    doc_p = sub.add_parser("doctor", help="Run pure-Python self-diagnosis checks")
    doc_p.set_defaults(func=cmd_doctor)

    args = parser.parse_args()

    if args.version:
        root = resolve_root(args.root) or Path.cwd()
        print(_read_version(root))
        sys.exit(0)

    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
