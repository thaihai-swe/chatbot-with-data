import json
import os
import glob


def read_thresholds(root):
    """Read Memory Promotion Thresholds from harness-config.yaml.

    Returns (early_warn, threshold_breach, hard_cap) as ints.
    Defaults: (100, 200, 3200)
    """
    import sys
    _lib_dir = os.path.dirname(os.path.abspath(__file__))
    if _lib_dir not in sys.path:
        sys.path.insert(0, _lib_dir)
    import yaml_reader

    cfg_path = os.path.join(root, 'core-zero', 'project', 'harness-config.yaml')
    early_warn, threshold_breach, hard_cap = 100, 200, 3200
    
    if os.path.exists(cfg_path):
        cfg = yaml_reader.load(cfg_path)
        th = cfg.get('thresholds', {})
        if 'memory_warn_lines' in th:
            early_warn = int(th['memory_warn_lines'])
        if 'memory_breach_lines' in th:
            threshold_breach = int(th['memory_breach_lines'])
        if 'memory_hard_lines' in th:
            hard_cap = int(th['memory_hard_lines'])

    return early_warn, threshold_breach, hard_cap


def build_path_map(root):
    """Build PATH_MAP for cross-file reference integrity checks.

    Scans core-zero/memories/repo/, core-zero/project/,
    core-zero/rules/, and core-zero/memories/domain/ for .md files.
    Returns {basename: relative_path}.
    """
    pm = {}
    base_dirs = [
        'core-zero/memories/repo',
        'core-zero/project',
        'core-zero/rules',
    ]
    for d in base_dirs:
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        for fn in sorted(os.listdir(full)):
            if fn.endswith('.md'):
                pm[fn] = os.path.join(d, fn)
    domain_dir = os.path.join(root, 'core-zero', 'memories', 'domain')
    if os.path.isdir(domain_dir):
        for dirpath, dirnames, filenames in os.walk(domain_dir):
            for fn in filenames:
                if fn.endswith('.md'):
                    rel = os.path.relpath(os.path.join(dirpath, fn), root)
                    pm[fn] = rel
    return pm


def check_manifest_drift(root):
    """Check manifest.json entries against files on disk.

    Returns 'OK' or a 'FAIL: ...' message string.
    """
    mf = os.path.join(root, 'manifest.json')
    if not os.path.exists(mf):
        return 'SKIP'

    with open(mf) as f:
        manifest = json.load(f)

    files = manifest.get('files', {})
    all_entries = files.get('overwrite', []) + files.get('copyIfMissing', [])

    manifest_files = set()
    for entry in all_entries:
        if entry.endswith('/'):
            continue
        full_pattern = os.path.join(root, entry)
        matches = glob.glob(full_pattern, recursive=True)
        for m in matches:
            if os.path.isfile(m):
                rel = os.path.relpath(m, root)
                manifest_files.add(rel)

    uncovered = set()
    exclude_prefixes = ('node_modules/', '.git/', '__pycache__/', '.corezero/')
    runtime_paths = ('artifacts/', 'core-zero/generated/', 'core-zero/memories/archive/')
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
        skip = False
        for p in exclude_prefixes:
            rp = rel_dir + '/' if rel_dir else ''
            if rp.startswith(p):
                skip = True
                break
        if skip:
            continue
        for fn in filenames:
            fpath = (rel_dir + '/' if rel_dir else '') + fn
            if fpath in manifest_files or fpath == 'manifest.json':
                continue
            if any(fpath.startswith(p) for p in runtime_paths):
                continue
            if fn.endswith(('.md', '.sh', '.py', '.json', '.yaml', '.yml', '.html', '.txt', '.template')):
                uncovered.add(fpath)

    missing_from_disk = []
    for f in sorted(manifest_files):
        if not os.path.exists(os.path.join(root, f)):
            missing_from_disk.append(f)
    for entry in all_entries:
        if entry.endswith('/') or any(c in entry for c in '*?['):
            continue
        if not os.path.exists(os.path.join(root, entry)):
            if entry not in missing_from_disk:
                missing_from_disk.append(entry)

    issues = []
    if missing_from_disk:
        issues.append('{} manifest entr{} missing from disk: {}'.format(
            len(missing_from_disk),
            'ies' if len(missing_from_disk) > 1 else 'y',
            ', '.join(missing_from_disk)))
    if uncovered:
        issues.append('{} file{} on disk not covered by manifest: {}'.format(
            len(uncovered),
            's' if len(uncovered) > 1 else '',
            ', '.join(sorted(uncovered)[:15]) + (' ...' if len(uncovered) > 15 else '')))

    if issues:
        return 'FAIL: ' + '; '.join(issues)
    return 'OK'
