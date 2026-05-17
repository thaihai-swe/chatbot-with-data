import logging
import json
import weaviate
import weaviate.classes as wvc
from typing import Optional, List, Tuple, Dict, Any
from indexing.base import VectorStore
from config import get_settings

logger = logging.getLogger(__name__)

class WeaviateVectorStore(VectorStore):
    """Weaviate implementation of the VectorStore ABC."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, collection_name: Optional[str] = None):
        settings = get_settings()
        self.url = url or settings.weaviate_url
        self.api_key = api_key or settings.weaviate_api_key
        self.collection_name = collection_name or settings.weaviate_collection_name

        self.client = weaviate.connect_to_local(
            host=self.url.split("//")[-1].split(":")[0],
            port=int(self.url.split(":")[-1]),
            headers={"X-OpenAI-Api-Key": settings.openai_api_key} if settings.openai_api_key else None,
            additional_config=wvc.init.AdditionalConfig(
                timeout=wvc.init.Timeout(init=30, query=60, insert=120)
            ),
            skip_init_checks=False # Set to True if gRPC still fails occasionally during start
        )
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists with the correct schema."""
        if not self.client.collections.exists(self.collection_name):
            logger.info(f"Creating Weaviate collection: {self.collection_name}")
            self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                properties=[
                    wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="document_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="collection_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="chunk_order", data_type=wvc.config.DataType.INT),
                    wvc.config.Property(name="parent_chunk_id", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="metadata_json", data_type=wvc.config.DataType.TEXT),
                ],
                inverted_index_config=wvc.config.Configure.inverted_index(
                    index_property_length=True,
                    index_timestamps=True,
                    index_null_state=True
                )
            )

    def add_vectors(self, vectors_data: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
        collection = self.client.collections.get(self.collection_name)

        with collection.batch.fixed_size(batch_size=100) as batch:
            for vector_id, embedding, metadata in vectors_data:
                properties = {
                    "text": metadata.get("text", ""),
                    "chunk_id": metadata.get("chunk_id"),
                    "document_id": metadata.get("document_id"),
                    "collection_id": metadata.get("collection_id"),
                    "chunk_order": metadata.get("chunk_order"),
                    "parent_chunk_id": metadata.get("parent_chunk_id"),
                    "metadata_json": json.dumps(metadata)
                }
                batch.add_object(
                    properties=properties,
                    vector=embedding,
                    uuid=vector_id
                )

        return len(vectors_data)

    def query_hybrid(
        self,
        query_text: str,
        query_embedding: List[float],
        alpha: float = 0.5,
        k: int = 10,
        collection_ids: Optional[List[str]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        collection = self.client.collections.get(self.collection_name)

        filters = None
        if collection_ids:
            if len(collection_ids) == 1:
                filters = wvc.query.Filter.by_property("collection_id").equal(collection_ids[0])
            else:
                filters = wvc.query.Filter.by_property("collection_id").contains_any(collection_ids)

        response = collection.query.hybrid(
            query=query_text,
            vector=query_embedding,
            alpha=alpha,
            limit=k,
            filters=filters,
            return_metadata=wvc.query.MetadataQuery(score=True, explain_score=True)
        )

        results = []
        for obj in response.objects:
            metadata = json.loads(obj.properties.get("metadata_json", "{}"))
            # Weaviate hybrid score is a combined score, not directly a similarity distance
            results.append((obj.properties.get("chunk_id"), obj.metadata.score, metadata))

        return results

    def delete_by_document(self, document_id: str) -> int:
        collection = self.client.collections.get(self.collection_name)
        result = collection.data.delete_many(
            where=wvc.query.Filter.by_property("document_id").equal(document_id)
        )
        return result.successful

    def delete_by_collection(self, collection_id: str) -> int:
        collection = self.client.collections.get(self.collection_name)
        result = collection.data.delete_many(
            where=wvc.query.Filter.by_property("collection_id").equal(collection_id)
        )
        return result.successful

    def count(self) -> int:
        collection = self.client.collections.get(self.collection_name)
        return collection.aggregate.over_all(total_count=True).total_count

    def clear_all(self) -> None:
        self.client.collections.delete(self.collection_name)
        self._ensure_collection()

    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()
