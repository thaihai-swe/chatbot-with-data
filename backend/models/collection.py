from dataclasses import dataclass


@dataclass
class Collection:
    collection_id: str
    name: str
    description: str | None
    routing_description: str | None
    is_default: bool
    created_at: str
    updated_at: str
