import json
import os
import fcntl
import tempfile
from datetime import datetime, timezone, timedelta


def records_path(root):
    return os.path.join(root, 'core-zero/memories/repo/harness-telemetry.jsonl')


def md_path(root):
    return os.path.join(root, 'core-zero/memories/repo/harness-telemetry.md')


def iter_records(root):
    fp = records_path(root)
    if not os.path.exists(fp):
        return
    with open(fp) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def count_open(root, task_id, feature=None):
    count = 0
    for rec in iter_records(root):
        if rec.get('task') == task_id and rec.get('status') == 'open':
            if feature is None or rec.get('feature') == feature:
                count += 1
    return count


def _next_id_from_records(records):
    max_num = 0
    for rec in records:
        if not isinstance(rec, dict):
            continue
        oid = rec.get('id', '')
        if oid.startswith('OBS-'):
            try:
                num = int(oid[4:])
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    return f'OBS-{max_num + 1:03d}'


def compute_next_id(root):
    """Unlocked scan — prefer append_record which allocates under flock."""
    return _next_id_from_records(list(iter_records(root)))


def append_record(root, task, feature, classification, description,
                  severity='medium', recurrence_risk='medium',
                  skill=None, root_cause=None):
    fp = records_path(root)
    os.makedirs(os.path.dirname(fp), exist_ok=True)

    # Create file if missing so we can exclusive-lock it for id allocation.
    if not os.path.exists(fp):
        open(fp, 'a').close()

    with open(fp, 'a+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            existing = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            record = {
                'id': _next_id_from_records(existing),
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'task': task,
                'feature': feature,
                'classification': classification,
                'severity': severity,
                'recurrence_risk': recurrence_risk,
                'description': description,
                'status': 'open',
                'fix_applied': 'none yet',
                'promotion_candidate': False,
            }
            if skill:
                record['skill'] = skill
            if root_cause:
                record['root_cause'] = root_cause
            f.seek(0, os.SEEK_END)
            f.write(json.dumps(record) + '\n')
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def update_record(root, record_id, status=None, fix_applied=None):
    fp = records_path(root)
    if not os.path.exists(fp):
        return

    records = []
    with open(fp) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append(line)

    found = False
    for i, rec in enumerate(records):
        if isinstance(rec, dict) and rec.get('id') == record_id:
            if status is not None:
                rec['status'] = status
            if fix_applied is not None:
                rec['fix_applied'] = fix_applied
            records[i] = rec
            found = True
            break

    if not found:
        return

    tmp = tempfile.NamedTemporaryFile(
        mode='w',
        dir=os.path.dirname(fp),
        prefix='.telemetry-tmp-',
        delete=False
    )
    try:
        with open(fp) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            for rec in records:
                if isinstance(rec, dict):
                    tmp.write(json.dumps(rec) + '\n')
                else:
                    tmp.write(rec + '\n')
            tmp.close()
            os.replace(tmp.name, fp)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        os.unlink(tmp.name)
        raise


def render_md(root):
    records = list(iter_records(root))
    out = md_path(root)

    total = len(records)
    open_count = sum(1 for r in records if r.get('status') == 'open')
    closed_count = total - open_count

    lines = []
    lines.append('# Harness Telemetry')
    lines.append('')
    lines.append(f'Total records: {total} | Open: {open_count} | Closed: {closed_count}')
    lines.append('')

    for rec in reversed(records):
        lines.append('---')
        lines.append(f'**ID:** {rec.get("id", "N/A")}')
        lines.append(f'**Timestamp:** {rec.get("timestamp", "N/A")}')
        lines.append(f'**Task:** {rec.get("task", "N/A")}')
        lines.append(f'**Feature:** {rec.get("feature", "N/A")}')
        lines.append(f'**Classification:** {rec.get("classification", "N/A")}')
        lines.append(f'**Severity:** {rec.get("severity", "N/A")}')
        lines.append(f'**Recurrence Risk:** {rec.get("recurrence_risk", "N/A")}')
        desc = rec.get('description', '')
        lines.append(f'**Description:** {desc[:80].replace("|", "/")}')
        lines.append(f'**Status:** {rec.get("status", "open")}')
        lines.append(f'**Fix Applied:** {rec.get("fix_applied", "none yet")}')
        lines.append('')

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write('\n'.join(lines))


def insights(root):
    records = list(iter_records(root))

    types = {}
    for rec in records:
        cls = rec.get('classification') or 'unknown'
        types[cls] = types.get(cls, 0) + 1
    top_failures = sorted(types.items(), key=lambda x: -x[1])[:5]

    high_risk = [rec for rec in records if rec.get('recurrence_risk') == 'high']

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    stale = []
    for rec in records:
        ts = rec.get('timestamp', '')
        if rec.get('status') != 'open':
            continue
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        try:
            rec_dt = datetime.fromisoformat(ts)
            if rec_dt < cutoff:
                stale.append(rec)
        except (ValueError, TypeError):
            continue

    return top_failures, high_risk, stale
