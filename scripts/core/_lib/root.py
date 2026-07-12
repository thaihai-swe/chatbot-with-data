import os

def resolve_root(hint=None):
    if hint and os.path.isdir(hint):
        candidates = [hint]
    else:
        candidates = [os.getcwd()]

    for start in candidates:
        current = os.path.abspath(start)
        while True:
            has_agents = os.path.isfile(os.path.join(current, 'AGENTS.md'))
            has_memories = os.path.isdir(os.path.join(current, 'core-zero/memories/repo'))
            if has_agents and has_memories:
                return current
            kit_dir = os.path.join(current, 'kit')
            has_kit_agents = os.path.isfile(os.path.join(kit_dir, 'AGENTS.md'))
            has_kit_memories = os.path.isdir(os.path.join(kit_dir, 'core-zero/memories/repo'))
            if has_kit_agents and has_kit_memories:
                return kit_dir
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
    return None
