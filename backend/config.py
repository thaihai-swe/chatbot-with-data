import os
from pathlib import Path


def build_config(overrides=None):
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / "data"

    config = {
        "TESTING": False,
        "DATA_DIR": str(data_dir),
        "UPLOAD_DIR": str(data_dir / "uploads"),
        "SQLITE_PATH": str(data_dir / "app.sqlite3"),
        "CHROMA_DIR": str(data_dir / "chroma"),
        "CHROMA_COLLECTION_PREFIX": "collection",
        "DEFAULT_CHUNK_SIZE": 512,
        "DEFAULT_CHUNK_OVERLAP": 64,
        "DEFAULT_EMBEDDING_MODEL": "local-hash-v1",
        "EMBEDDING_DIMENSIONS": 32,
        "URL_TIMEOUT_SECONDS": 30,
        "DEFAULT_CHAT_RETRIEVAL_MODE": "semantic",
        "CHAT_RETRIEVAL_TOP_K": 5,
        "HYBRID_SEMANTIC_WEIGHT": 0.6,
        "HYBRID_KEYWORD_WEIGHT": 0.4,
        "CHAT_CONTEXT_TOKEN_BUDGET": 200,
        "CHAT_HISTORY_MAX_MESSAGES": 6,
        "ANSWERABILITY_MIN_SIMILARITY": 0.5,
        "ANSWERABILITY_MIN_CHUNK_COUNT": 1,
        "ANSWERABILITY_MIN_QUERY_OVERLAP": 0.15,
        "ANSWERABILITY_CONSISTENCY_THRESHOLD": 0.8,
        "GENERATION_PROVIDER": "openai-responses-v1",
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "OPENAI_REASONING_EFFORT": os.getenv("OPENAI_REASONING_EFFORT", "low"),
        "SAFETY_WARN_RISK_THRESHOLD": 30,
        "SAFETY_LOWER_TRUST_RISK_THRESHOLD": 55,
        "SAFETY_EXCLUDE_RISK_THRESHOLD": 70,
        "SAFETY_REFUSE_RISK_THRESHOLD": 90,
        "SAFETY_MULTI_ISSUE_REFUSE_TOTAL": 130,
        "SAFETY_RULE_PATTERNS": [
            {
                "name": "ignore_previous_instructions",
                "pattern": r"(ignore|disregard|forget)\s+(all\s+)?(previous|earlier|prior)\s+(instructions?|rules?)",
                "risk_score": 95,
            },
            {
                "name": "override_system_prompt",
                "pattern": r"(system prompt|developer message|hidden instructions?)",
                "risk_score": 88,
            },
            {
                "name": "reveal_secrets",
                "pattern": r"(reveal|print|show).*(prompt|secret|api key|token|credential)",
                "risk_score": 92,
            },
            {
                "name": "suppress_citations",
                "pattern": r"(without citations|do not cite|ignore citations?)",
                "risk_score": 76,
            },
            {
                "name": "instruction_rewrite",
                "pattern": r"(you are now|new instructions?|override.*rules?)",
                "risk_score": 62,
            },
        ],
    }

    if overrides:
        config.update(overrides)

    return config
